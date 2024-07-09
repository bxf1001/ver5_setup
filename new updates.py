    






    def search_user(self):
        self.timer1_input.clear()
        self.timer2_input.clear()
        self.timer3_input.clear()
        self.contact_text_browser.clear()
        self.selected_contacts.clear()
        self.progress_label.setText("Call Not in Progress")
        self.timer1_input.setEnabled(False)
        self.timer2_input.setEnabled(False)
        self.timer3_input.setEnabled(False)
        self.connect_button.setEnabled(True)
        self.connect_button.setStyleSheet("""
    QPushButton {
        background-color: #50DA59;  /* Green background */
        border: none;  /* No border */
        color: white;  /* White text */
        padding: 15px 32px;  /* Padding */
        text-align: center;  /* Centered text */
        text-decoration: none;  /* No underline */
        font-size: 18px;
        margin: 4px 2px;
          /* Mouse pointer changes when over button */
        border-radius: 4px;  /* Rounded corners */
    }

    QPushButton:hover {
        background-color: #45a049;  /* Green background on hover */
    }

    QPushButton:pressed {
        background-color: #2e7d32;  /* Darker green background when pressed */
    }
""")
        
        # Define the primary and alternative database file paths
        with open('datas/url.json') as f:
            url = json.load(f)
    
        primary_db = url['data_path']
        alternative_db = url['data_path2']


        # Connect to the database
        if os.path.exists(primary_db):
            conn = sqlite3.connect(primary_db)
        else:
            conn = sqlite3.connect(alternative_db)

        c = conn.cursor()
    
        # Get the user ID from the input field
        user_id = self.user_id_input.text()
    
        # Select the user's details from the users table
        c.execute("SELECT name, phone1, phone2, phone3 FROM users WHERE id = ?", (user_id,))
    
        # Fetch the first row from the result
        row = c.fetchone()
    
        # Close the connection
        conn.close()

def timestamped_data(self, contact):
        user_id = self.user_id_input.text()
        add_timer1 = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
        # Check if user_id exists in user_data
        if user_id not in self.user_data:
            # If user_id does not exist, create a new dictionary for it
            self.user_data[user_id] = {}
    
        self.user_data[user_id]['number'] = contact  # Use 'number' instead of ['number']
        print(f"{self.user_data[user_id]['number']} (Called at {add_timer1})")
    
        # Rest of your code...
        # Get the path to the last recording

        try:
            with open(r'datas\url.json', 'r') as f:
                path_data = json.load(f)
                recordings_folder =  r"{}".format(path_data.get('path', 'recordings'))  # Use get method to avoid KeyError
                print(f"Recordings folder: {recordings_folder}")
        except FileNotFoundError:
            QMessageBox.information(self, 'Error', 'Please set the path to the recordings folder in the settings.')


        recording_files = os.listdir(recordings_folder)
        last_recording = sorted(recording_files)[-1]  # Assumes files are named in a way that allows sorting
        
        timestamped_data = {
            "user_id": user_id,
            "name" : self.user_data[user_id].get('name', 'Unknown'),  # Use get method to avoid KeyError
            "number": self.user_data[user_id]['number'],
            "timestamp": add_timer1,
            "recording": os.path.join(recordings_folder, last_recording)
        }
        
        with open(r'datas\timestamped_data.json', 'a') as f:
            json.dump(timestamped_data, f)
            f.write('\n')  # Add a newline for readability