from typing import Optional
import datetime

from sqlalchemy import Date, ForeignKeyConstraint, Identity, Integer, PrimaryKeyConstraint, Unicode, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = 'Author'
    __table_args__ = (
        PrimaryKeyConstraint('Id', name='PK__Author__3214EC074BF44A88'),
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    Name: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    Book: Mapped[list['Book']] = relationship('Book', back_populates='Author_')


class Category(Base):
    __tablename__ = 'Category'
    __table_args__ = (
        PrimaryKeyConstraint('Id', name='PK__Category__3214EC07FD56332A'),
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    Name: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    Book: Mapped[list['Book']] = relationship('Book', back_populates='Category_')


class Book(Base):
    __tablename__ = 'Book'
    __table_args__ = (
        ForeignKeyConstraint(['Author_Id'], ['Author.Id'], name='FK__Book__Author_Id__3C69FB99'),
        ForeignKeyConstraint(['Category_Id'], ['Category.Id'], name='FK__Book__Category_I__3D5E1FD2'),
        PrimaryKeyConstraint('Id', name='PK__Book__3214EC07008C587B')
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    Title: Mapped[str] = mapped_column(Unicode(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    ISBN: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
    Published_Year: Mapped[Optional[int]] = mapped_column(Integer)
    Status: Mapped[Optional[str]] = mapped_column(Unicode(20, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('available')"))
    Author_Id: Mapped[Optional[int]] = mapped_column(Integer)
    Category_Id: Mapped[Optional[int]] = mapped_column(Integer)

    Author_: Mapped[Optional['Author']] = relationship('Author', back_populates='Book')
    Category_: Mapped[Optional['Category']] = relationship('Category', back_populates='Book')
    Borrow: Mapped[list['Borrow']] = relationship('Borrow', back_populates='Book_')


class Borrow(Base):
    __tablename__ = 'Borrow'
    __table_args__ = (
        ForeignKeyConstraint(['Book_Id'], ['Book.Id'], name='FK__Borrow__Book_Id__403A8C7D'),
        PrimaryKeyConstraint('Id', name='PK__Borrow__3214EC07D8C2888C')
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True)
    User_Id: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
    Book_Id: Mapped[Optional[int]] = mapped_column(Integer)
    Borrow_Date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    Return_Date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    Status: Mapped[Optional[str]] = mapped_column(Unicode(20, 'SQL_Latin1_General_CP1_CI_AS'), server_default=text("('borrowing')"))

    Book_: Mapped[Optional['Book']] = relationship('Book', back_populates='Borrow')

