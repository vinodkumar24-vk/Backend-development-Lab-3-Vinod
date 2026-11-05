const express = require('express');
const path = require('path');

let sqlite = null;
let sqlite3 = null;
try {
  sqlite = require('sqlite');
  sqlite3 = require('sqlite3');
} catch (e) {
  console.log('Running in serverless/fallback mode without native sqlite3 binary');
}

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const PORT = process.env.PORT || 3000;
const dbPath = path.join(__dirname, 'books.db');

let db = null;

// Initial seed books (used for in-memory fallback if native SQLite is unavailable)
let inMemoryBooks = [
  { id: 1, title: 'Atomic Habits', author: 'James Clear', price: 499, pages: 320 },
  { id: 2, title: 'Deep Work', author: 'Cal Newport', price: 450, pages: 304 },
  { id: 3, title: 'Python Crash Course', author: 'Eric Matthes', price: 850, pages: 544 },
  { id: 4, title: 'Fluent Python', author: 'Luciano Ramalho', price: 1150, pages: 792 },
  { id: 5, title: 'Operating System Concepts', author: 'Peter B. Galvin', price: 990, pages: 976 },
  { id: 6, title: 'Computer Networking: A Top-Down Approach', author: 'James Kurose', price: 1100, pages: 864 },
  { id: 7, title: 'Learning SQL', author: 'Alan Beaulieu', price: 550, pages: 380 },
  { id: 8, title: 'System Design Interview', author: 'Alex Xu', price: 1250, pages: 300 },
  { id: 9, title: 'Structure and Interpretation of Computer Programs', author: 'Harold Abelson', price: 1300, pages: 657 },
  { id: 10, title: 'Automate the Boring Stuff with Python', author: 'Al Sweigart', price: 680, pages: 504 }
];

// Database initialization
const initializeDBAndServer = async () => {
  try {
    if (sqlite && sqlite3) {
      db = await sqlite.open({
        filename: dbPath,
        driver: sqlite3.Database
      });
      console.log('Connected to SQLite database successfully');

      // Auto-create table and seed if table does not exist
      await db.run(`
        CREATE TABLE IF NOT EXISTS book (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL,
          author TEXT NOT NULL,
          price INTEGER NOT NULL,
          pages INTEGER NOT NULL
        );
      `);

      const bookCount = await db.get('SELECT COUNT(*) AS count FROM book;');
      if (bookCount.count === 0) {
        for (const b of inMemoryBooks) {
          await db.run(
            'INSERT INTO book (title, author, price, pages) VALUES (?, ?, ?, ?);',
            [b.title, b.author, b.price, b.pages]
          );
        }
        console.log('Seeded database with initial books.');
      }
    }

    if (!process.env.VERCEL) {
      app.listen(PORT, () => {
        console.log(`Server Running at http://localhost:${PORT}/`);
      });
    }
  } catch (error) {
    console.error(`DB Error: ${error.message}`);
    if (!process.env.VERCEL) {
      process.exit(1);
    }
  }
};

initializeDBAndServer();

// Task 1 & 6: Root Welcome Route
app.get('/', (request, response) => {
  response.status(200).json({
    message: 'Books REST API (Lab 3) - Vinod Kumar',
    student: {
      name: 'VINOD KUMAR',
      regNo: '252U1R1184',
      section: 'CSE-2D(214)',
      faculty: 'Joel Prashanth D',
      course: 'Backend Development Fundamentals (Year II Term II)'
    },
    endpoints: {
      getAllBooks: 'GET /books?search_q=&order_by=price&order=ASC&limit=5&offset=0&min_price=400&max_price=900',
      getSingleBook: 'GET /books/:bookId',
      createBook: 'POST /books',
      updateBook: 'PUT /books/:bookId',
      deleteBook: 'DELETE /books/:bookId'
    }
  });
});

// Task 1, 2, 3: GET /books - Search, Sort, Filter & Pagination
app.get(['/books', '/books/'], async (request, response, next) => {
  try {
    const {
      search_q = '',
      order_by = 'id',
      order = 'ASC',
      limit = 10,
      offset = 0,
      min_price,
      max_price
    } = request.query;

    // Allowed columns and ordering directions to prevent SQL Injection
    const allowedColumns = ['id', 'title', 'author', 'price', 'pages'];
    const safeOrderBy = allowedColumns.includes(order_by.toLowerCase())
      ? order_by.toLowerCase()
      : 'id';

    const safeOrder = order.toUpperCase() === 'DESC' ? 'DESC' : 'ASC';

    const parsedLimit = parseInt(limit) > 0 ? parseInt(limit) : 10;
    const parsedOffset = parseInt(offset) >= 0 ? parseInt(offset) : 0;

    if (db) {
      let query = `
        SELECT
          id,
          title,
          author,
          price,
          pages
        FROM
          book
        WHERE
          title LIKE ?
      `;
      const queryParams = [`%${search_q}%`];

      // Price range filters
      if (min_price !== undefined && max_price !== undefined) {
        query += ` AND price BETWEEN ? AND ?`;
        queryParams.push(parseInt(min_price), parseInt(max_price));
      } else if (min_price !== undefined) {
        query += ` AND price >= ?`;
        queryParams.push(parseInt(min_price));
      } else if (max_price !== undefined) {
        query += ` AND price <= ?`;
        queryParams.push(parseInt(max_price));
      }

      // Safe sorting and pagination
      query += ` ORDER BY ${safeOrderBy} ${safeOrder} LIMIT ? OFFSET ?;`;
      queryParams.push(parsedLimit, parsedOffset);

      const booksList = await db.all(query, queryParams);
      return response.status(200).json(booksList);
    }

    // In-memory fallback
    let filtered = inMemoryBooks.filter((b) =>
      b.title.toLowerCase().includes(search_q.toLowerCase())
    );

    if (min_price !== undefined && max_price !== undefined) {
      filtered = filtered.filter(
        (b) => b.price >= parseInt(min_price) && b.price <= parseInt(max_price)
      );
    } else if (min_price !== undefined) {
      filtered = filtered.filter((b) => b.price >= parseInt(min_price));
    } else if (max_price !== undefined) {
      filtered = filtered.filter((b) => b.price <= parseInt(max_price));
    }

    filtered.sort((a, b) => {
      let valA = a[safeOrderBy];
      let valB = b[safeOrderBy];
      if (typeof valA === 'string') {
        return safeOrder === 'ASC'
          ? valA.localeCompare(valB)
          : valB.localeCompare(valA);
      }
      return safeOrder === 'ASC' ? valA - valB : valB - valA;
    });

    const paginated = filtered.slice(parsedOffset, parsedOffset + parsedLimit);
    return response.status(200).json(paginated);
  } catch (error) {
    next(error);
  }
});

// Task 1, 5, 6: GET /books/:bookId - Get Single Book by ID
app.get(['/books/:bookId', '/books/:bookId/'], async (request, response, next) => {
  try {
    const { bookId } = request.params;
    const numericId = parseInt(bookId);

    if (isNaN(numericId) || numericId <= 0) {
      return response.status(400).json({ message: 'Invalid book ID parameter' });
    }

    if (db) {
      const getBookQuery = `SELECT * FROM book WHERE id = ?;`;
      const book = await db.get(getBookQuery, [numericId]);

      if (!book) {
        return response.status(404).json({ message: 'Requested Book Not Found' });
      }
      return response.status(200).json(book);
    }

    const book = inMemoryBooks.find((b) => b.id === numericId);
    if (!book) {
      return response.status(404).json({ message: 'Requested Book Not Found' });
    }
    return response.status(200).json(book);
  } catch (error) {
    next(error);
  }
});

// Task 1, 4, 5, 6: POST /books - Add a New Book with Validation
app.post(['/books', '/books/'], async (request, response, next) => {
  try {
    const { title, author, price, pages } = request.body;

    // Validation 1: Title
    if (!title || typeof title !== 'string' || title.trim() === '') {
      return response.status(400).json({
        message: 'Title is required and must be a non-empty string'
      });
    }

    // Validation 2: Author
    if (!author || typeof author !== 'string' || author.trim() === '') {
      return response.status(400).json({
        message: 'Author is required and must be a non-empty string'
      });
    }

    // Validation 3: Price
    const parsedPrice = Number(price);
    if (price === undefined || isNaN(parsedPrice) || parsedPrice <= 0) {
      return response.status(400).json({
        message: 'Price is required and must be a positive number'
      });
    }

    // Validation 4: Pages
    const parsedPages = Number(pages);
    if (pages === undefined || !Number.isInteger(parsedPages) || parsedPages <= 0) {
      return response.status(400).json({
        message: 'Pages is required and must be a positive integer'
      });
    }

    if (db) {
      const insertBookQuery = `
        INSERT INTO
          book (title, author, price, pages)
        VALUES
          (?, ?, ?, ?);
      `;
      const dbResult = await db.run(insertBookQuery, [
        title.trim(),
        author.trim(),
        parsedPrice,
        parsedPages
      ]);
      return response.status(201).json({
        message: 'Book Added Successfully',
        bookId: dbResult.lastID
      });
    }

    const newId =
      inMemoryBooks.length > 0
        ? Math.max(...inMemoryBooks.map((b) => b.id)) + 1
        : 1;
    const newBook = {
      id: newId,
      title: title.trim(),
      author: author.trim(),
      price: parsedPrice,
      pages: parsedPages
    };
    inMemoryBooks.push(newBook);
    return response.status(201).json({
      message: 'Book Added Successfully',
      bookId: newId
    });
  } catch (error) {
    next(error);
  }
});

// Task 1, 5, 6: PUT /books/:bookId - Update Existing Book
app.put(['/books/:bookId', '/books/:bookId/'], async (request, response, next) => {
  try {
    const { bookId } = request.params;
    const numericId = parseInt(bookId);

    if (isNaN(numericId) || numericId <= 0) {
      return response.status(400).json({ message: 'Invalid book ID parameter' });
    }

    const { title, author, price, pages } = request.body;

    if (db) {
      const existing = await db.get('SELECT * FROM book WHERE id = ?;', [numericId]);
      if (!existing) {
        return response.status(404).json({ message: 'Requested Book Not Found' });
      }

      // Validate optional fields if provided
      if (price !== undefined && (isNaN(Number(price)) || Number(price) <= 0)) {
        return response.status(400).json({
          message: 'Price must be a positive number'
        });
      }
      if (pages !== undefined && (!Number.isInteger(Number(pages)) || Number(pages) <= 0)) {
        return response.status(400).json({
          message: 'Pages must be a positive integer'
        });
      }

      const updatedTitle = title !== undefined && typeof title === 'string' && title.trim() !== ''
        ? title.trim()
        : existing.title;
      const updatedAuthor = author !== undefined && typeof author === 'string' && author.trim() !== ''
        ? author.trim()
        : existing.author;
      const updatedPrice = price !== undefined ? Number(price) : existing.price;
      const updatedPages = pages !== undefined ? Number(pages) : existing.pages;

      const updateBookQuery = `
        UPDATE
          book
        SET
          title = ?,
          author = ?,
          price = ?,
          pages = ?
        WHERE
          id = ?;
      `;
      await db.run(updateBookQuery, [
        updatedTitle,
        updatedAuthor,
        updatedPrice,
        updatedPages,
        numericId
      ]);
      return response.status(200).json({ message: 'Book Updated Successfully' });
    }

    const index = inMemoryBooks.findIndex((b) => b.id === numericId);
    if (index === -1) {
      return response.status(404).json({ message: 'Requested Book Not Found' });
    }

    if (price !== undefined && (isNaN(Number(price)) || Number(price) <= 0)) {
      return response.status(400).json({ message: 'Price must be a positive number' });
    }
    if (pages !== undefined && (!Number.isInteger(Number(pages)) || Number(pages) <= 0)) {
      return response.status(400).json({ message: 'Pages must be a positive integer' });
    }

    inMemoryBooks[index] = {
      ...inMemoryBooks[index],
      title: title !== undefined && typeof title === 'string' && title.trim() !== '' ? title.trim() : inMemoryBooks[index].title,
      author: author !== undefined && typeof author === 'string' && author.trim() !== '' ? author.trim() : inMemoryBooks[index].author,
      price: price !== undefined ? Number(price) : inMemoryBooks[index].price,
      pages: pages !== undefined ? Number(pages) : inMemoryBooks[index].pages
    };
    return response.status(200).json({ message: 'Book Updated Successfully' });
  } catch (error) {
    next(error);
  }
});

// Task 1, 5, 6: DELETE /books/:bookId - Delete Book
app.delete(['/books/:bookId', '/books/:bookId/'], async (request, response, next) => {
  try {
    const { bookId } = request.params;
    const numericId = parseInt(bookId);

    if (isNaN(numericId) || numericId <= 0) {
      return response.status(400).json({ message: 'Invalid book ID parameter' });
    }

    if (db) {
      const existing = await db.get('SELECT * FROM book WHERE id = ?;', [numericId]);
      if (!existing) {
        return response.status(404).json({ message: 'Requested Book Not Found' });
      }

      await db.run('DELETE FROM book WHERE id = ?;', [numericId]);
      return response.status(200).json({ message: 'Book Deleted Successfully' });
    }

    const index = inMemoryBooks.findIndex((b) => b.id === numericId);
    if (index === -1) {
      return response.status(404).json({ message: 'Requested Book Not Found' });
    }

    inMemoryBooks.splice(index, 1);
    return response.status(200).json({ message: 'Book Deleted Successfully' });
  } catch (error) {
    next(error);
  }
});

// 404 Handler for undefined routes
app.use((request, response) => {
  response.status(404).json({ message: 'Endpoint Not Found' });
});

// Global 500 Error Handler
app.use((error, request, response, next) => {
  console.error('Unhandled Server Error:', error);
  response.status(500).json({
    message: 'Internal Server Error',
    error: error.message
  });
});

module.exports = app;
