import streamlit as st
import pandas as pd
import csv
import os
from cryptography.fernet import Fernet, InvalidToken, InvalidSignature

# Function to load the encryption key
def load_key():
    try:
        with open('secret.key', 'rb') as file:
            return file.read()
    except FileNotFoundError:
        st.error("Encryption key file ('secret.key') not found. Run the app once to generate it.")
        return None

# Generate and save a random encryption key
def generate_key():
    key = Fernet.generate_key()
    with open('secret.key', 'wb') as file:
        file.write(key)
        st.success("Encryption key generated and saved to 'secret.key'")

def main():
    # Check for the existence of the encryption key
    if not os.path.exists('secret.key'):
        generate_key()

    key = load_key()

    if key:
        cipher_suite = Fernet(key)

        st.title("Appointment Reservation System")
        
        # Input fields for appointment reservation
        name = st.text_input("Your Name")
        date = st.date_input("Appointment Date", min_value=pd.to_datetime("today"))
        time = st.time_input("Appointment Time")
        service = st.selectbox("Service Required", ["Consultation", "Therapy", "Follow-Up", "Health Check"])

        # Button to save the appointment
        if st.button("Reserve Appointment"):
            if not name or not date or not time or not service:
                st.error("Please fill in all fields before reserving an appointment.")
            else:
                try:
                    # Encrypt the appointment data
                    appointment_data = f"{name},{date},{time},{service}"
                    encrypted_data = cipher_suite.encrypt(appointment_data.encode())

                    # Save the encrypted appointment data to a CSV file
                    with open('appointments.csv', 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([encrypted_data.decode()])
                    st.success("Appointment reserved successfully!")
                    
                    # Clear the input fields
                    name = ""
                    date = pd.to_datetime("today")
                    time = None
                    service = ""
                except Exception as e:
                    st.error(f"Error reserving appointment: {e}")

        # Button to read and display appointments
        if st.button("View Appointments"):
            try:
                df = pd.read_csv('appointments.csv', header=None)
                decrypted_data = []
                for index, row in df.iterrows():
                    try:
                        decrypted_text = cipher_suite.decrypt(row[0].encode()).decode()
                        decrypted_data.append(decrypted_text.split(','))
                    except (InvalidToken, InvalidSignature) as e:
                        st.error(f"Error decrypting row {index + 1}: {e}. Check your key or data file.")
                        continue
                df_decrypted = pd.DataFrame(decrypted_data, columns=['Name', 'Date', 'Time', 'Service'])
                st.dataframe(df_decrypted)
            except FileNotFoundError:
                st.info("No appointments found.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Entry point of the application
if __name__ == "__main__":
    main()
