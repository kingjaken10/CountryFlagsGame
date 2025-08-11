from tkinter import messagebox
from PIL import Image
import customtkinter as ctk
from customtkinter import*
import pygame
import os
import random
import json
import sys
import copy

# directory containing flag images
FLAG_DIR = "flags"

# creating list of world regions
regions = ["Africa", "Asia", "Caribbean", "Europe", "North America", "Oceania", "South America", "All Countries"]

class CountryFlagsGame:

    # constructor
    def __init__(self, root, data = None):
        # set up window
        self.root = root    # get main window
        self.root.title("Country Flags Game")   # set window title
        self.root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")   # make window take up full screen
        self.root.resizable(False, False)   # make window non-resizable

        # center align window
        root.update_idletasks() # force GUI update
        width = root.winfo_width()  # get window width
        height = root.winfo_height()    # get window height
        x = (root.winfo_screenwidth() - width) // 2 + 180 # calculate x position
        y = (root.winfo_screenheight() - height) // 2 + 108  # calculate y position
        root.geometry(f'{width}x{height}+{x}+{y}')  # set window size and position

        # variables
        self.data = data    # a dictionary that will store the content of the JSON file
        self.score = 0  # user score
        self.total_questions = 0    # total number of questions
        self.current_question = 0   # current question number
        self.num_answers = 4    # default number of answer choices
        self.countries_dict = {}    # stores the data that maps a country's code to its name
        self.correct_answer = None # stores the correct answer

        # initialize flag label and answer choice buttons
        self.flag_label = ctk.CTkLabel(self.root, text="", fg_color="transparent", bg_color="transparent") # create a label that will display the flag image
        self.button1 = ctk.CTkButton(self.root, text="Button 1", width=375, height=50, command=lambda: self.check_answer(0), font=("System", 20), corner_radius=10, fg_color=("#3B8ED0","#1F6AA5"), text_color="white", hover_color="#093254")  # create a button
        self.button2 = ctk.CTkButton(self.root, text="Button 2", width=375, height=50, command=lambda: self.check_answer(1), font=("System", 20), corner_radius=10, fg_color=("#3B8ED0","#1F6AA5"), text_color="white", hover_color="#093254")  # create a button
        self.button3 = ctk.CTkButton(self.root, text="Button 3", width=375, height=50, command=lambda: self.check_answer(2), font=("System", 20), corner_radius=10, fg_color=("#3B8ED0","#1F6AA5"), text_color="white", hover_color="#093254")  # create a button
        self.button4 = ctk.CTkButton(self.root, text="Button 4", width=375, height=50, command=lambda: self.check_answer(3), font=("System", 20), corner_radius=10, fg_color=("#3B8ED0","#1F6AA5"), text_color="white", hover_color="#093254")  # create a button

        # load country data
        self.file_path = "AllCountries.json"    # file to be read

        if os.path.exists(self.file_path):
            self.read_json_file(self.file_path) # file found, read file
        else:
            messagebox.showerror("ERROR", f"File not found: {self.file_path}")  # file not found, display error message  
            sys.exit()  # exit the program

        # add widgets to main window
        self.create_widgets()   # create other widgets

        # initialize score label
        self.score_label = ctk.CTkLabel(self.root, width=100, height=50, text="Questions Answered: 0 | Correct: 0 | Percentage: 0.00%") # create score label
        self.score_label.configure(font=("System", 20), fg_color="slategray4", text_color="white", corner_radius=20)    # customize look
        self.score_label.grid(row=6, column=0, columnspan=5, pady=10)   # add and position score label

        # hide all buttons initially
        self.hide_buttons()


    def read_json_file(self, file_path):
        # open and read the JSON file into a dictionary
        try:
            # open and read the file
            with open(file_path, "r") as file:
                self.data = json.load(file) # store the result in the dictionary self.data
        except FileNotFoundError:
            print(f"ERROR: The file at {file_path} was not found")  # file not found, print error message
        except json.JSONDecodeError:
            print(f"ERROR: The file could not be decoded. Check if it's a valid JSON file.")    # file is not a valid JSON, print error message
        except Exception as e:
            print(f"An unexpected error occurred: {e}") # some exception is thrown, print error message
    

    def create_widgets(self):
        # create a label frame for the region, number of answer choices, and number of questions
        input_frame = ctk.CTkFrame(self.root, fg_color="slategray4") # create label frame
        input_frame.grid(row=0, column=0, rowspan=2, columnspan = 5, sticky="ns", padx=10, pady=20) # position label frame

        # configure grid columns for proper alignment
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        # add label for region
        self.region = ctk.StringVar()    # create a StringVar object that stores the region
        ctk.CTkLabel(input_frame, text="Region", font=("System", 18), fg_color="transparent", text_color="black").grid(row=0, column=0) # create and postion label for region

        # add combo box for region
        self.region_combo = ctk.CTkComboBox(input_frame, variable=self.region, state="readonly", width=140, command=self.load_num_of_questions)   # create combo box whose result is stored in self.region
        self.region_combo.configure(values=regions)   # populate combo box so options are items found in the list self.regions
        self.region_combo.configure(font=("System", 18), dropdown_font=("System", 18), fg_color=("#3B8ED0","#1F6AA5"), border_color=("#3B8ED0","#1F6AA5"), button_color=("#36719F", "#144870")) # customize look
        self.region_combo.grid(row=1, column=0, padx=35, pady=5, sticky="w")  # add and position combo box
        self.region_combo.set("Select a Region")    # set default text on combo box
        
        # add label for number of answer choices
        ctk.CTkLabel(input_frame, text="Number of Answer Choices", font=("System", 18), fg_color="transparent", text_color="black").grid(row=0, column=1, padx=15)  # create and postion label for number of answer choices
        
        # add CTkOptionMenufor number of answer choices
        num_answer_options = ["1", "2", "3", "4"]  # options for CTkOptionMenu
        self.num_answers_var = ctk.StringVar(value="4")  # set default value for number of answer choices to 4
        self.num_answers_menu = ctk.CTkOptionMenu(input_frame, variable=self.num_answers_var, values=num_answer_options)    # create CTkOptionMenu whose result is stored in self.num_answers_var
        self.num_answers_menu.configure(font=("System", 18), dropdown_font=("System", 18))  # customize look
        self.num_answers_menu.grid(row=1, column=1, pady=5, sticky="s") # add and position CTkOptionMenu
        
        # add label for number of questions
        ctk.CTkLabel(input_frame, text="Number of Questions", font=("System", 18), fg_color="transparent", text_color="black").grid(row=0, column=2, padx=35)  # create and postion label for number of questions

        # add CTkOptionMenu for number of questions
        num_question_options = ["5", "10", "20", "30"]
        self.num_questions_var = ctk.StringVar(value="5")   # set default value for number of questions to 5
        self.num_of_questions = ctk.CTkOptionMenu(input_frame, variable=self.num_questions_var, values=num_question_options)    # create CTkOptionMenu whose result is stored in self.num_questions_var
        self.num_of_questions.configure(font=("System", 18), dropdown_font=("System", 18))  # customize look
        self.num_of_questions.grid(row=1, column=2, padx=35, pady=5, sticky="e") # add and position CTkOptionMenu
        
        # add start button
        self.start_button = ctk.CTkButton(input_frame, text="START QUIZ", command=self.start_quiz, font=("System", 18), width=50)  # create start button
        self.start_button.grid(row=2, column=1, padx=20, pady=10, sticky="w")    # add and position start button

        # add reset button
        self.reset_button = ctk.CTkButton(input_frame, text="RESET", command=self.reset_quiz, font=("System", 18), width=50)    # create reset button
        self.reset_button.grid(row=2, column=1, padx=20, pady=10, sticky="e")    # add and position reset button


    def load_num_of_questions(self, event):
        selected_region = self.region.get() # get the region

        region_data = copy.deepcopy(self.data[selected_region]) # get the info (code and name) of the countries in the selected region
        max_entries = len(region_data)  # get the number of countries in the selected region
        self.update_option_menu(max_entries)    # update option menu


    def update_option_menu(self, max_value):
        # generate the series based on max_value
        series = self.generate_series(max_value)    # get the possible options for number of questions

        # add the new options from series to the CTkOptionMenu
        self.num_of_questions.configure(values=series)

        # set default value to the first item in the series
        self.num_questions_var.set(series[0])
        

    def generate_series(self, max_value):
        # handle cases where max_value is less than 10
        if max_value < 10:
            return [str(max_value)] # return a list with 1 option: max_value
        
        # handle cases where max_value is between 10 and 20 (exclusive)
        if max_value < 20:
            return [str(5), str(10), str(max_value)]    # return a list with 3 options: 5, 10, and max_value
        
        # base series for values greater than or equal to 20
        base_series = [5, 10, 20, 30]  # list of base options

        # handle case where max_value is less than or equal to the last element in base_series
        if max_value <= base_series[-1]:
            # create a series with values from base_series that are less than max_value
            series = [x for x in base_series if x < max_value]

            # append max_value to the series
            series.append(max_value)
        else:
            # extend the base series to include max_value
            series = base_series + [max_value]

        # ensure the series contains no more than five elements
        while len(series) > 5:
            series.pop(0)   # discard the first element in the series
        
        return [str(num) for num in series] # return the series as strings


    def hide_buttons(self):
        # hide all answer choice buttons
        self.button1.grid_forget()  # hide button1
        self.button2.grid_forget()  # hide button2
        self.button3.grid_forget()  # hide button3
        self.button4.grid_forget()  # hide button4


    def show_buttons(self):
        self.hide_buttons() # hide all buttons before showing specific ones
        
        if self.num_answers == 1:
            # show 1 button
            self.button1.grid(row=3, column=1, pady=20)

            # reposition score label
            self.score_label.grid(row=6, column=0, columnspan=5, pady=20)

        elif self.num_answers == 2:
            # show 2 buttons
            self.button1.grid(row=3, column=1, padx=0, pady=20, sticky="w")
            self.button2.grid(row=3, column=1, padx=0, pady=20, sticky="e")

            # reposition score label
            self.score_label.grid(row=6, column=0, columnspan=5, pady=20)

        elif self.num_answers == 3:
            # show 3 buttons
            self.button1.grid(row=3, column=1, padx=0, pady=20, sticky="w")
            self.button2.grid(row=3, column=1, padx=300, pady=20)
            self.button3.grid(row=3, column=1, padx=0, pady=20, sticky="e")

            # reposition score label
            self.score_label.grid(row=6, column=0, columnspan=5, pady=20)

        elif self.num_answers == 4:
            # show 4 buttons
            self.button1.grid(row=3, column=1, padx=0, pady=20, sticky="w")
            self.button2.grid(row=3, column=1, padx=0, pady=20, sticky="e")
            self.button3.grid(row=4, column=1, padx=0, pady=0, sticky="w")
            self.button4.grid(row=4, column=1, padx=0, pady=0, sticky="e")

            # reposition score label
            self.score_label.grid(row=6, column=0, columnspan=5, pady=40)


    def start_quiz(self):
        selected_region = self.region_combo.get()   # get selected region

        # check if a region is selected
        if selected_region == "Select a Region":
            # a region was not selected
            messagebox.showerror("ERROR", "Select a Region!")   # display error message
            return
        
        # play music
        self.start_music()
        
        # get questions for selected region, data is already randomized
        num_questions = int(self.num_questions_var.get())   # get number of questions
        self.get_countries_by_region(selected_region, num_questions)    # populate self.countries_dict with countries in the selected region 

        # set initial values
        self.current_question = 0   # set current question to 0
        self.score = 0  # set score to 0
        self.num_answers = int(self.num_answers_var.get())  # get number of answer choices
        self.load_images() # load flag images
        self.start_new_challenge()  # update the screen with buttons and score board
        self.ask_questions(num_questions)   # start asking questionss

    
    def get_countries_by_region(self, region_name, num_questions_left):
        self.countries_dict = {} # reset dictionary's contents

        # check if selected region is in dictionary self.data
        if region_name in self.data:
            # region found in dictionary
            region_data = copy.deepcopy(self.data[region_name]) # make a deep copy of that region's data

            # populate self.countries_dict with countries in the selected region
            for _ in range(len(region_data) + 1):
                # check if region_data is empty
                if not region_data:
                    # region_data is empty
                    break   # exit for loop
                
                count = len(region_data)    # get current number of countries in region_data
                index = random.randint(0, count-1)  # generate a random index
                item = region_data[index]   # get country (country code and country name) at specified index 
                self.countries_dict[item["country_code"]] = item["country_name"] # map item's country code to its country name in self.countries_dict
                region_data.pop(index)  # remove the country at the specified index from region_data (prevent duplicates)
        else:
            # region does not exist, return an empty dictionary
            return {}


    def load_images(self):
        self.flags = [] # list of tuples that store the country code and path to the flag image

        # get list of all filenames in FLAG_DIR
        filenames = [f.lower() for f in os.listdir(FLAG_DIR) if f.endswith(".png")]

        # extract country codes from self.countries_dict
        country_codes = self.countries_dict.keys()

        # loop through all country codes
        for code in country_codes:
            filename = f"{code.lower()}.png"    # construct the expected filename
            
            # check if filename is found in list filenames
            if filename in filenames:
                try:
                    # store the code and path to the flag image
                    self.flags.append((code, os.path.join(FLAG_DIR, filename)))
                except Exception as e:
                    # exception is thrown
                    print(f"Error loading image {filename}: {e}")   # print error message
    

    def start_new_challenge(self):
        self.show_buttons() # display multiple choice buttons
        self.update_score_board()   # update score board
    

    def update_score_board(self):
        num_questions_value = int(self.num_questions_var.get()) # get number of questions

        percentage = (self.score / num_questions_value) * 100   # calculate score as a percentage
        self.score_label.configure(text=f"Questions Answered: {self.current_question} | Correct: {self.score} | Percentage: {percentage:.2f}%")   # update score label


    def ask_questions(self, num_questions):
        # check if question cap has been reached
        if self.current_question >= num_questions:
            # question cap reached
            self.show_final_score() # display final score
            self.reset_quiz()   # reset the quiz
            return
        
        # update score board
        self.update_score_board()

        option_list = []    # list that will store the answer choices

        # update question number
        self.current_question += 1

        # get a country from the region
        flag_code, flag_path = self.flags[self.current_question-1]  # get country's code and path and store in flag_code and flag_path respectively
        correct_country = self.countries_dict[flag_code]    # store name of correct country 

        country_list = list(self.countries_dict.values())   # get values (country names) of countries_dict
        country_list.remove(correct_country)    # remove the current country from the list
        option_list.append(correct_country) # add the current country to the list of answer choices

        # get other answer choices and remove possibility of duplicates
        for _ in range(self.num_answers-1):
            # check if country_list is empty
            if not country_list:
                # country_list is empty
                break   # exit for loop
            
            # get another answer choice
            index = random.randint(0, len(country_list)-1)  # generate a random number for the index
            option_list.append(country_list[index]) # add the country at the specified index to option_list
            country_list.remove(country_list[index]) # remove the country at the specified index from country_list to prevent duplicates

        # shuffle the answer choices and determine the correct answer
        random.shuffle(option_list) # shuffle the answer choices
        self.correct_answer = option_list.index(correct_country)    # get index of correct answer

        # load and display the flag image
        pil_image = Image.open(flag_path)   # load flag image into PIL Image object
        pil_image = pil_image.resize((650, 420), Image.LANCZOS) # resize image
        self.flag_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(650, 420)) # convert PILImage object into CTkImage object to display on CTkinter widget (self.flag_label)
        self.flag_label.configure(image=self.flag_image)    # update label by setting its image to self.flag_image
        self.flag_label.grid(row=2, column=0, columnspan=5, padx=10, pady=5, sticky="n")   # add and position label on window

        # put answer choices on buttons
        self.button1.configure(text=option_list[0] if len(option_list) > 0 else "")    # update button1
        self.button2.configure(text=option_list[1] if len(option_list) > 1 else "")    # update button2
        self.button3.configure(text=option_list[2] if len(option_list) > 2 else "")    # update button3
        self.button4.configure(text=option_list[3] if len(option_list) > 3 else "")    # update button4


    def show_final_score(self):
        # stop music from playing game
        self.stop_music()

        # play congratulations song
        music_file = "songs/congratulations.mp3"  # path to music file
        pygame.mixer.music.load(music_file) # load mixer with music file
        pygame.mixer.music.play(1) # play music file once
        pygame.mixer.music.fadeout(8500)    # play music file for 9.4 seconds

        num_questions = int(self.num_questions_var.get())   # get number of questions
        percentage = (self.score / num_questions) * 100 # calculate score as a percentage
        messagebox.showinfo("Quiz Completed", f"Final Score: {self.score}/{num_questions}\nPercentage: {percentage:.2f}%")  # display that quiz was completed and stats
        self.score_label.configure(text=f"Questions Answered: {num_questions} | Correct: {self.score} | Percentage: {percentage:.2f}%") # update score label


    def check_answer(self, selected_option):
        # reset all button colors to default color
        self.button1.configure(fg_color=("#3B8ED0","#1F6AA5"), text_color="white", hover_color="#093254")
        self.button2.configure(fg_color=("#3B8ED0","#1F6AA5"), text_color="white", hover_color="#093254")
        self.button3.configure(fg_color=("#3B8ED0","#1F6AA5"), text_color="white", hover_color="#093254")
        self.button4.configure(fg_color=("#3B8ED0","#1F6AA5"), text_color="white", hover_color="#093254")

        # check if self.correct_answer is a valid index
        if 0 <= self.correct_answer < self.num_answers:
            # self.correct_answer is a valid index
            correct_button = [self.button1, self.button2, self.button3, self.button4][self.correct_answer]  # determine which button has the correct answer
        else:
            # self.correct_answer is not a valid index
            print(f"Invalid correct_answer index: {self.correct_answer}")   # print error message
            return
        
        # color the correct button green
        correct_button.configure(fg_color="#2FA572", hover_color="#2FA572")

        # check if the selected button is correct or not
        if selected_option == self.correct_answer:
            # selected button is correct
            self.score += 1 # add to score
        else:
            # selected button is wrong, color button red
            [self.button1, self.button2, self.button3, self.button4][selected_option].configure(fg_color="#E74747", hover_color="#E74747")

        # update score board
        self.update_score_board()

        # wait for 1 second and then call self.reset_button_colors
        self.root.after(1000, self.reset_button_colors)

        # ask next question
        num_questions = self.num_questions_var.get()  # get number of questions
        self.root.after(1000, self.ask_questions, int(num_questions))   # call self.ask_questions after 1 second


    def reset_quiz(self):
        # check if mixer has been initialized
        if pygame.mixer.get_init() is None:
            self.region_combo.set("Select a Region")    # reset to default text
            self.num_answers_var.set(value=4)    # reset to default option
            self.num_questions_var.set(value=5) # reset to default option
            return

        # stop music
        self.stop_music()

        # hide self.flag_label
        self.flag_label.grid_forget()

        # reset values
        self.score = 0  # set score to 0
        self.current_question = 0   # set current question to 0
        self.region_combo.set("Select a Region")    # reset to default text
        self.num_answers_var.set(value=4)    # reset to default option
        self.num_questions_var.set(value=5) # reset to default option
        self.score_label.grid(row=6, column=0, columnspan=5, pady=10)   # reposition score label
        self.update_option_menu(30) # reset to default option menu
        self.hide_buttons() # hide all buttons
        self.update_score_board()   # update score board


    def reset_button_colors(self):
        # reset all button colors
        self.button1.configure(fg_color=("#3B8ED0","#1F6AA5"), text_color="white", hover_color="#093254")
        self.button2.configure(fg_color=("#3B8ED0","#1F6AA5"), text_color="white", hover_color="#093254")
        self.button3.configure(fg_color=("#3B8ED0","#1F6AA5"), text_color="white", hover_color="#093254")
        self.button4.configure(fg_color=("#3B8ED0","#1F6AA5"), text_color="white", hover_color="#093254")


    def start_music(self):
        self.mixer = pygame.mixer.init() # initialize mixer
        music_file = "songs/Jump Up, Super Star! Music Box Version.mp3"  # path to music file
        pygame.mixer.music.load(music_file) # load mixer with music file
        pygame.mixer.music.play(-1) # loop music file continuously


    def stop_music(self):
        pygame.mixer.music.stop()   # stop music


if __name__ == "__main__":
    root = CTk()  # create main window
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = CountryFlagsGame(root) # create instance of CountryFlagsGame class
    root.mainloop() # keeps window running and interactive
