from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class ResearchItem(Base):
    __tablename__ = "research"
    id = Column(Integer, primary_key=True)
    source = Column(String(50))
    competitor = Column(String(100))
    content = Column(Text)
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Idea(Base):
    __tablename__ = "ideas"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    body = Column(Text)
    status = Column(String(20), default="pending")
    rejection_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    contents = relationship("Content", back_populates="idea")

class Content(Base):
    __tablename__ = "content"
    id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"))
    type = Column(String(20))
    file_path = Column(String(500))
    caption = Column(Text)
    status = Column(String(20), default="pending")
    rejection_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    idea = relationship("Idea", back_populates="contents")
    posts = relationship("Post", back_populates="content")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey("content.id"))
    platform = Column(String(30))
    platform_post_id = Column(String(200), nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="scheduled")
    reach = Column(Integer, default=0)
    engagement = Column(Integer, default=0)
    content = relationship("Content", back_populates="posts")

class Approval(Base):
    __tablename__ = "approvals"
    id = Column(Integer, primary_key=True)
    item_type = Column(String(20))
    item_id = Column(Integer)
    decision = Column(String(20))
    notes = Column(Text, nullable=True)
    decided_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class WebsiteChange(Base):
    __tablename__ = "website_changes"
    id = Column(Integer, primary_key=True)
    change_type = Column(String(50))
    description = Column(Text)
    payload = Column(JSON)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(50))
    status = Column(String(20))
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    log = Column(Text, nullable=True)


class SocialSnapshot(Base):
    __tablename__ = "social_snapshots"
    id          = Column(Integer, primary_key=True, index=True)
    platform    = Column(String, nullable=False)       # instagram / facebook / tiktok
    handle      = Column(String, nullable=False)
    followers   = Column(Integer, default=0)
    following   = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    bio         = Column(String, default="")
    scraped_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SocialPostCache(Base):
    __tablename__ = "social_posts_cache"
    id            = Column(Integer, primary_key=True, index=True)
    platform      = Column(String, nullable=False)
    post_id       = Column(String, nullable=False, unique=True)
    likes         = Column(Integer, default=0)
    comments      = Column(Integer, default=0)
    thumbnail_url = Column(String, default="")
    caption       = Column(String, default="")
    posted_at     = Column(DateTime, nullable=True)
    scraped_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))
