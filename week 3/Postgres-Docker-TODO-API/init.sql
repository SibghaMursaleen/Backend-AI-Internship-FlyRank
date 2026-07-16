CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    done BOOLEAN DEFAULT FALSE
);

-- Create a B-Tree index on the title column for query optimization
CREATE INDEX IF NOT EXISTS idx_tasks_title ON tasks(title);

-- Insert initial seed tasks matching the original in-memory data
INSERT INTO tasks (title, done) VALUES
('Buy groceries', FALSE),
('Read a book', TRUE),
('Work out', FALSE);

