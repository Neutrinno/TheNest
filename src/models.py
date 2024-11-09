from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, func

metadata = MetaData()

users = Table(
   "users",
    metadata,
    Column("id", Integer, primary_key = True),
    Column("email", String, nullable = False),
    Column("registered_at", TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
    Column("hashed_password", String(length=1024), nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
)

information = Table(
   "information",
    metadata,
    Column("id", Integer, primary_key = True),
    Column("student_id", Integer, ForeignKey(users.c.id)),
    Column("full_name", String, nullable = False),
    Column("email", String, nullable = False),
    Column("admission_score", Integer, nullable=False),
)


dormitory = Table(
    "dormitory",
    metadata,
    Column("id", Integer, primary_key = True),
    Column("name", String, nullable = False),
    Column("address", String, nullable = False),
    Column("filled", String, nullable = False),
)


room = Table(
    "room",
    metadata,
    Column("id", Integer, primary_key = True),
    Column("dormitory_id", Integer, ForeignKey(dormitory.c.id)),
    Column("room_number", String, default=False, nullable=False), #Это может вызвать ощшибку, обати на это внимание
    Column("floor", Integer, default=False, nullable=False),
    Column("capacity", Integer, default=False, nullable=False),
    Column("filled", Boolean, default=False, nullable=False),
)


bad = Table(
    "bad",
    metadata,
    Column("id", Integer, primary_key = True), #Над этим тоже нужно буджет подумать
    Column("room_id", Integer, ForeignKey(room.c.id)),
    Column("is_occupied", Boolean, default=False, nullable=False),
)


assignment = Table(
    "assignment",
    metadata,
    Column("id", Integer, primary_key = True),
    Column("student_id", Integer, ForeignKey(users.c.id)),
    Column("bad_id", Integer, ForeignKey(bad.c.id)),
    Column("application_status", String, nullable = False),
)


application = Table(
    "application",
    metadata,
    Column("id", Integer, primary_key = True),
    Column("student_id", Integer, ForeignKey(users.c.id)),
    Column("preferred_dormitory_id", Integer),
    Column("preferred_floor", Integer),
    Column("submission_date", TIMESTAMP, nullable = False),
)


status = Table(
    "status",
    metadata,
    Column("application_id", Integer, ForeignKey(application.c.id)),
    Column("student_id", Integer, ForeignKey(users.c.id)),
    Column("status", String, nullable = False),
)


roommate_preference = Table(
    "roommate_preference",
    metadata,
    Column("id", Integer, primary_key = True),
    Column("application_id", Integer, ForeignKey(application.c.id)),
    Column("preferred_student_id", Integer, ForeignKey(users.c.id)),
)