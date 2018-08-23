import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://lijguuuketxvgt:41b5b754c093cc173bad3e5b5ac739efe2531630ea7b1a501a6dfb3a8bd3fed9@ec2-54-83-13-119.compute-1.amazonaws.com:5432/deo34sags8udmk")
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv") #opens the file
    reader = csv.reader(f) #reads the csv file
    for isbn, title, author, bookyear in reader: #looping over every line the reader is going to read // inserting in the loop
        db.execute("INSERT INTO books (isbn, title, author, bookyear) VALUES (:isbn, :title, :author, :bookyear)",
                    {"isbn": isbn, "title": title, "author": author, "bookyear": bookyear})
        print(f"Added books with isbn {isbn} called {title} by {author} released in {bookyear}.")
    db.commit()

if __name__ == "__main__":
    main()
