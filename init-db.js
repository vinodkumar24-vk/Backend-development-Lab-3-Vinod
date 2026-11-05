const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, 'books.db');

const initialBooks = [
  { title: 'Atomic Habits', author: 'James Clear', price: 499, pages: 320 },
  { title: 'Deep Work', author: 'Cal Newport', price: 450, pages: 304 },
  { title: 'Python Crash Course', author: 'Eric Matthes', price: 850, pages: 544 },
  { title: 'Fluent Python', author: 'Luciano Ramalho', price: 1150, pages: 792 },
  { title: 'Operating System Concepts', author: 'Peter B. Galvin', price: 990, pages: 976 },
  { title: 'Computer Networking: A Top-Down Approach', author: 'James Kurose', price: 1100, pages: 864 },
  { title: 'Learning SQL', author: 'Alan Beaulieu', price: 550, pages: 380 },
  { title: 'System Design Interview', author: 'Alex Xu', price: 1250, pages: 300 },
  { title: 'Structure and Interpretation of Computer Programs', author: 'Harold Abelson', price: 1300, pages: 657 },
  { title: 'Automate the Boring Stuff with Python', author: 'Al Sweigart', price: 680, pages: 504 }
];

const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error connecting to database:', err.message);
    process.exit(1);
  }
  console.log('Connected to SQLite database for initialization.');
});

db.serialize(() => {
  db.run('DROP TABLE IF EXISTS book;', (err) => {
    if (err) console.error('Error dropping table:', err.message);
  });

  const createTableQuery = `
    CREATE TABLE book (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      author TEXT NOT NULL,
      price INTEGER NOT NULL,
      pages INTEGER NOT NULL
    );
  `;

  db.run(createTableQuery, (err) => {
    if (err) {
      console.error('Error creating table:', err.message);
      return;
    }
    console.log('Table "book" created successfully.');

    const insertStmt = db.prepare(
      'INSERT INTO book (title, author, price, pages) VALUES (?, ?, ?, ?);'
    );

    initialBooks.forEach((book) => {
      insertStmt.run([book.title, book.author, book.price, book.pages], (insertErr) => {
        if (insertErr) {
          console.error(`Error inserting "${book.title}":`, insertErr.message);
        }
      });
    });

    insertStmt.finalize(() => {
      console.log(`Successfully seeded ${initialBooks.length} books into the database.`);
      db.close();
    });
  });
});

