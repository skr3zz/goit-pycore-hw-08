from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name can't be empty")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():
            self.__value = value
        else:
            raise ValueError('Invalid phone number')


class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        self.phones = [p for p in self.phones if str(p) != phone_number]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return "Phone number edited successfully"
        return "Phone number not found"

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday):
        try:
            self.birthday = Birthday(birthday)
        except ValueError:
            print(f'Некоректна дата народження для користувача {self.name.value}')

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    import pickle

    def save_data(self, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.data, f)
        print(f"Data saved to {filename}")

    def load_data(book,filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                book.data = pickle.load(f)
        except FileNotFoundError:
            pass
    
    def main():
        book = AddressBook()
        book.load_data()
        print("Welcome to the assistant bot!")
        while True:
            user_input = input("Enter a command: ")
            command, args = parse_input(user_input)

            if command in ["close", "exit"]:
                book.save_data()  
                print("Good bye!")
                break

            elif command == "hello":
                book.save_data()
                print("How can I help you?")

            elif command == "add":
                book.save_data()
                print(add_contact(args, book))

            elif command == "change":
                book.save_data()
                print(change_contact(args, book))

            elif command == "phone":
                book.save_data()
                if len(args) != 1:
                    print("Invalid command format. Use 'phone [name]'")
                else:
                    name = args[0]
                    if name not in book:
                        print("Contact not found.")
                    else:
                        print(f"Phone number for {name}: {book[name]}")
                    
            elif command == "all":
                book.save_data()
                print(show_all(book))

            elif command == "add-birthday":
                book.save_data()
                print(add_birthday(args, book))
            
            elif command == "show-birthday":
                book.save_data()
                print(show_birthday(args, book))

            elif command == "birthdays":
                book.save_data()
                print(birthdays(args, book))

            else:
                book.save_data()
                print("Invalid command.")

    
    @staticmethod
    def find_next_weekday(d, weekday: int):
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return d + timedelta(days=days_ahead)

    @staticmethod
    def get_upcoming_birthdays(users, find_next_weekday):
        upcoming_birthdays = []
        days = 7
        today = datetime.today().date()

        for user in users:
            try:
                birthday = datetime.strptime(user.birthday.value, '%d.%m.%Y').date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                if 0 <= (birthday_this_year - today).days <= days:
                    if birthday_this_year.weekday() >= 5:
                        birthday_this_year = find_next_weekday(birthday_this_year, 0)

                    congratulation_date_str = birthday_this_year.strftime('%d.%m.%Y')
                    upcoming_birthdays.append({
                        "name": user.name.value,
                        "congratulation_date": congratulation_date_str
                    })
            except ValueError:
                print(f'Некоректна дата народження для користувача {user.name.value}')
        return upcoming_birthdays

    def birthdays(self, find_next_weekday):
        return self.get_upcoming_birthdays(self.data.values(), find_next_weekday)

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def show_all_contacts(self):
        if self.data:
            contacts_info = "\n".join([f"{record.name.value}: {', '.join([phone.value for phone in record.phones])}" for record in self.data.values()])
            return f"All contacts:\n{contacts_info}"
        else:
            return "Address book is empty."


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "KeyError"
        except ValueError:
            return "ValueError"
        except IndexError:
            return "IndexError"
    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    if len(args) != 3:
        return "Invalid command format. Use 'change [name] [old_phone] [new_phone]'"

    name, old_phone, new_phone = args
    record = book.find(name)

    if record:
        try:
            record.edit_phone(old_phone, new_phone)
            return f"Phone number updated for {name}"
        except ValueError:
            return f"Invalid phone number format. Please use 10 digits."

    return f"Contact '{name}' not found."


@input_error
def show_phones(args, book: AddressBook):
    if len(args) != 1:
        return "Invalid command format. Use 'show_phones [name]'"

    name = args[0]
    record = book.find(name)

    if record:
        if record.phones:
            return f"Phone numbers for {name}: {', '.join([phone.value for phone in record.phones])}"
        else:
            return f"No phone numbers found for {name}."
    else:
        return f"Contact '{name}' not found."


@input_error
def show_all(book: AddressBook):
    if book.data:
        contacts_info = "\n".join([f"{record.name.value}: {', '.join([phone.value for phone in record.phones])}" for record in book.data.values()])
        return f"All contacts:\n{contacts_info}"
    else:
        return "Address book is empty."


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        return f"Contact '{name}' not found."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday.date.strftime('%d.%m.%Y')}"
    elif record:
        return f"{name} doesn't have a birthday."
    else:
        return f"Contact '{name}' not found."


@input_error
def birthdays(args, book):
    upcoming_birthdays = book.birthdays(AddressBook.find_next_weekday)
    if upcoming_birthdays:
        return "Upcoming birthdays:\n" + "\n".join(
            [f"{record['name']}: {record['congratulation_date']}" for record in upcoming_birthdays]
        )
    else:
        return "No upcoming birthdays."


def parse_input(user_input):
    parts = user_input.strip().split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1].split() if len(parts) > 1 else []
    return command, args


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            if len(args) != 1:
                print("Invalid command format. Use 'phone [name]'")
            else:
                name = args[0]
                if name not in book:
                    print("Contact not found.")
                else:
                    print(f"Phone number for {name}: {book[name]}")

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")



if __name__ == "__main__":
    main()