// A few important global variables
let nav = 0;
let clicked = null;
let events = localStorage.getItem('events') ? JSON.parse(localStorage.getItem('events')) : [];

// Global Constants for the file
const apiUrl = 'http://localhost:8887';
const calendar = document.getElementById('calendar');
const newEventModal = document.getElementById('newEventModal');
const deleteEventModal = document.getElementById('deleteEventModal');
const backDrop = document.getElementById("modalBackDrop");
const eventTitleInput = document.getElementById('eventTitleInput');
const nameInput = document.getElementById('nameInput');
const emailInput = document.getElementById('emailInput');
const descriptionInput = document.getElementById('descriptionTextArea');
const weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

/**
 * Function to open the modal for the date that was clicked on
 * @param {*} date The date that was slected
 */
function openModal(date)
{
    // TODO: This needs to be update to support the type of inteface that we actually want for the booking
    clicked = date;

    const eventForDay = events.find(e => e.date == clicked);

    if (eventForDay)
    {
        document.getElementById('eventText').innerText = eventForDay.title;
        deleteEventModal.style.display = 'block';
    }
    else
    {
        newEventModal.style.display = 'block';
    }

    backDrop.style.display = 'block';
}

/**
 * This is the main function of the webage to make it reload and refesh the page with the new and updated information
 */
async function load()
{
    // Finding the current date
    const dt = new Date();

    if (nav !== 0)
    {
        dt.setMonth(new Date().getMonth() + nav);
    }

    // Collecting information about the current day
    const day = dt.getDate();
    const month = dt.getMonth();
    const year = dt.getFullYear();

    // Collecting information about the current month
    const firstDayOfMonth = new Date(year, month, 1);
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // Creating a string version of the date that will be used later
    const dateString = firstDayOfMonth.toLocaleDateString('en-us', {
        weekday: 'long',
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
    });

    // Finding the number of padding days that need to be blank to corretly represent the first day
    const paddingDays =  weekdays.indexOf(dateString.split(', ')[0]);

    document.getElementById('monthDisplay').innerText = 
        `${dt.toLocaleDateString('en-us', {month: 'long'})} ${year}`;
    
    calendar.innerHTML = '';

    const params = new URLSearchParams({ month: `${month + 1}`});

    const response = await fetch(`${apiUrl}/event?${params}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
    });

    const events = await response.json();

    console.log(response);
    console.log(events);

    // Rendering all fo the days of the current month
    for(let i = 1; i <= paddingDays + daysInMonth; i++)
    {
        const daySquare =  document.createElement('div');
        daySquare.classList.add('day');

        const dayString = `${month + 1}/${i - paddingDays}/${year}`;

        if (i > paddingDays)
        {
            daySquare.innerText = i - paddingDays;
            
            if (response.ok)
            {

                const dayEvents = events.filter(event => event.day === dayString);

                for (const event of dayEvents) 
                {
                    const eventDiv = document.createElement('div');
                    eventDiv.classList.add('event');
                    eventDiv.innerText = event.title;
                    daySquare.appendChild(eventDiv);
                }
            }

            if (i - paddingDays === day && nav === 0)
            {
                daySquare.id = 'currentDay';
            }

            daySquare.addEventListener('click', () => openModal(dayString));
        }
        else
        {
            daySquare.classList.add('padding');
        }

        calendar.appendChild(daySquare);
    }
    
}

/**
 * Closing any modal that is open
 */
function closeModal()
{
    // TODO: Will need to update this since this is not the desired way that our menu will function
    newEventModal.style.display = 'none';
    deleteEventModal.style.display = 'none';
    backDrop.style.display = 'none';
    eventTitleInput.value = '';
    eventTitleInput.classList.remove('error');
    nameInput.value = '';
    nameInput.classList.remove('error');
    emailInput.value = '';
    emailInput.classList.remove('error');
    descriptionInput.value = '';
    descriptionInput.classList.remove('error');
    clicked = null;
    load();
}

/**
 * This is the function that will handle saving a new event
 */
async function saveEvent()
{
    let valid = true;
    // TODO: Will need to edit this to talk to the new api

    // Validating the input from the user
    if (!nameInput.value)
    {
        nameInput.classList.add('error');
        valid = false;
    }
    else
    {
        nameInput.classList.remove('error');
    }

    if (!eventTitleInput.value)
    {
        eventTitleInput.classList.add('error');
        valid = false;
    }
    else
    {
        eventTitleInput.classList.remove('error');
    }

    if (!emailInput.value || !emailInput.value.endsWith("@georgefox.edu"))
    {
        emailInput.classList.add('error');
        valid = false;
    }
    else
    {
        emailInput.classList.remove('error');
    }

    if(valid)
    {
                
        const eventData = {
            event_id: 1,
            title: eventTitleInput.value,
            organizer: nameInput.value,
            size: 25,
            day: clicked,
            time_start: 7,
            time_end: 8,
            description: descriptionInput.value,
        };

        const response = await fetch(`${apiUrl}/event`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(eventData)
        });

        const data = await response.json();

        console.log(eventData);
        console.log(data);

        eventTitleInput.classList.remove('error');

        localStorage.setItem('events', JSON.stringify(events));
        closeModal();
    }
}

/**
 * Function to delete an event from the calendar
 */
function deleteEvent()
{
    // TODO: This method might not be needed at all, might update or delete it later 
    events = events.filter(e => e.date !== clicked);
    localStorage.setItem('events', JSON.stringify(events));
    closeModal();
}

/**
 * Function to initiate all the button event listeners
 */
function initButtons()
{
    // TODO: Specific buttons will proabably change, but the idea of this method will still remain the same
    document.getElementById('nextButton').addEventListener('click', () => {
        nav++;
        load();
    });
    document.getElementById('backButton').addEventListener('click', () => {
        nav--;
        load();
    });

    document.getElementById('saveButton').addEventListener('click', saveEvent);
    document.getElementById('cancelButton').addEventListener('click', closeModal);

    document.getElementById('deleteButton').addEventListener('click', deleteEvent);
    document.getElementById('closeButton').addEventListener('click', closeModal);
}

/*
 * This is the code that is acutally run when the porgram is initialized
 */
initButtons();
load();