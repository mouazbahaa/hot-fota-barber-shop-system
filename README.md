# 🪒 HOT FOTA 💈 — Barbershop Management System

An **OOP** Python project for managing a barbershop called **HOT FOTA**:
services + a shopping cart (just like a supermarket cart) + appointment
booking + a database that stores data for every customer who uses the
system + a simple smart assistant that suggests services and time slots.

The interface is fully **Dark Mode**, styled with a barber-tool vibe
(razor ✂️, barber pole 💈, hot towel ♨️) throughout every tab.

## Requirements
- Python 3.9+ (Tkinter and sqlite3 come bundled with Python, no extra install needed)

## Running it
```bash
python main.py
```
On first run, a `barbershop.db` file is created automatically in the same
folder, pre-filled with default services and barbers.

## File structure
| File | Purpose |
|---|---|
| `models.py` | The classes: `Service`, `Customer`, `Barber`, `Cart`, `Appointment` |
| `database.py` | All SQLite interactions (registering customers, services, bookings) |
| `ai_assistant.py` | The "Smart Assistant" that suggests services/times, pluggable to a real AI |
| `main.py` | The Tkinter GUI tying everything together |

## Using the system (interface tabs)
1. **Login**: Create a new account (name + phone + password) or log in with
   an existing one. Your data is stored in the database and comes back
   every time you log in again.
2. **Services & Cart**: Pick a service (haircut / beard / haircut & beard /
   hot towel...) and add it to the cart just like a supermarket cart — the
   total price updates automatically. There's a suggestion from the smart
   assistant below the cart.
3. **Booking**: Choose a barber and date, you'll only see the available
   slots (booked ones are automatically removed from the list), pick a
   slot and click confirm.
4. **My Appointments**: Shows all your bookings, and you can cancel any
   of them.
5. **Shop Management**: A screen for the shop owner to see all bookings
   (for every customer), with the option to filter by a specific date.

## The Smart Assistant (AI)
Right now it runs on simple local rules with no internet needed (e.g.,
suggesting a hot towel if it's not already in the cart, or recommending
the best available time slot).

If you'd like to upgrade it to a real AI model (like Claude via the
Anthropic API), open `ai_assistant.py` and check the `get_ai_suggestion`
method — it has a ready example of how to wire it up.

## Ideas for future expansion
- Add a separate admin password for the management tab.
- Link actual service duration to booking multiple consecutive slots
  instead of a single fixed slot.
- Add SMS/WhatsApp reminders for the customer before their appointment.
