CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL,
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    hashed_password VARCHAR(1024) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_superuser BOOLEAN DEFAULT FALSE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL
);

CREATE TABLE dormitory (
    id SERIAL PRIMARY KEY,
    address VARCHAR NOT NULL,
    quantity_floor INTEGER NOT NULL,
    quantity_place INTEGER NOT NULL,
    is_occupied BOOLEAN DEFAULT FALSE NOT NULL
);

CREATE TABLE room (
    id SERIAL PRIMARY KEY,
    dormitory_id INTEGER REFERENCES dormitory(id),
    room_number VARCHAR NOT NULL,
    floor INTEGER NOT NULL,
    capacity INTEGER NOT NULL,
    is_occupied BOOLEAN DEFAULT FALSE NOT NULL
);

CREATE TABLE bed (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES room(id),
    is_occupied BOOLEAN DEFAULT FALSE NOT NULL
);

CREATE TABLE assignment (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id),
    bed_id INTEGER REFERENCES bed(id),
    application_status VARCHAR NOT NULL
);

CREATE TABLE application (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id),
    first_name VARCHAR NOT NULL,
    surname VARCHAR NOT NULL,
    middle_name VARCHAR,
    admission_score INTEGER NOT NULL,
    preferred_dormitory INTEGER,
    preferred_floor INTEGER,
    submission_date TIMESTAMP NOT NULL,
    first_preferred_student VARCHAR,
    second_preferred_student VARCHAR,
    third_preferred_student VARCHAR
);

CREATE TABLE status (
    application_id INTEGER REFERENCES application(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES users(id),
    status VARCHAR NOT NULL,
    PRIMARY KEY (application_id)
);

CREATE TABLE student_listing (
    student_id INTEGER PRIMARY KEY,
    admission_score INTEGER NOT NULL,
    status VARCHAR NOT NULL,
    wishes BOOLEAN NOT NULL
);