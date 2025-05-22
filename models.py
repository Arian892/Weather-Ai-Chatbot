from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class QueryHistory(Base):
    __tablename__ = 'query_history'

    id = Column(Integer, primary_key=True)
    user_query = Column(Text)
    agent_response = Column(Text)
    city = Column(String)
    date = Column(String)  # You can also use DateTime if needed
    timestamp = Column(DateTime, default=datetime.utcnow)

def load_recent_history(limit=5):
    session = Session()
    # Get last N queries ordered by timestamp descending
    history = session.query(QueryHistory).order_by(QueryHistory.timestamp.desc()).limit(limit).all()
    session.close()

    # Format as simple strings to prepend as context
    formatted_history = []
    for record in reversed(history):  # reverse so oldest is first
        formatted_history.append(
            f"User: {record.user_query}\nAssistant: {record.agent_response}"
        )
    return "\n\n".join(formatted_history)


def log_query_to_db(query, response, city=None, date=None):
    session = Session()
    record = QueryHistory(
        user_query=query,
        agent_response=response,
        city=city,
        date=date
    )
    print(f"Logging query to DB: {query}, {response}")
    session.add(record)
    session.commit()
    session.close()


# SQLite setup
engine = create_engine("sqlite:///weather_history.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
