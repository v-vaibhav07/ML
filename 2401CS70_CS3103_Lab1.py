import csv
import os
import smtplib
import getpass
from datetime import datetime
from email.mime.text import MIMEText

se = input("Enter your Gmail address: ")
sp = getpass.getpass("Enter your App Password: ") 

sf = 'students.csv'
af = 'attendance.csv'
cf = 'complaints.csv'

bc = 2500
pmr = 65

mu = {
    'Monday': {'Breakfast': 'Poha', 'Lunch': 'Dal Chawal', 'Dinner': 'Roti Sabzi'},
    'Tuesday': {'Breakfast': 'Idli', 'Lunch': 'Rajma Chawal', 'Dinner': 'Paneer Sabzi'},
    'Wednesday': {'Breakfast': 'Aloo Paratha', 'Lunch': 'Chole Bhature', 'Dinner': 'Khichdi'},
    'Thursday': {'Breakfast': 'Upma', 'Lunch': 'Kadhi Pakora', 'Dinner': 'Mix Veg'},
    'Friday': {'Breakfast': 'Dosa', 'Lunch': 'Veg Biryani', 'Dinner': 'Egg Curry / Dal'},
    'Saturday': {'Breakfast': 'Puri Sabzi', 'Lunch': 'Fried Rice', 'Dinner': 'Noodles'},
    'Sunday': {'Breakfast': 'Uttapam', 'Lunch': 'Special Thali', 'Dinner': 'Pav Bhaji'}
}

def initialize_files():
    if not os.path.exists(sf):
        with open(sf, mode='w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['roll_number', 'name', 'mailid', 'hostel'])
            
    if not os.path.exists(af):
        with open(af, mode='w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['roll_number', 'date', 'meal_type', 'status'])
            
    if not os.path.exists(cf):
        with open(cf, mode='w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['complaint_id', 'roll_number', 'date', 'complaint_text', 'status'])

def send_email(to, sub, bdy):
    if se == "your_email@gmail.com":
        print("[Warning] Email not sent. Please configure SENDER_EMAIL and SENDER_PASSWORD.")
        return
    try:
        m = MIMEText(bdy)
        m['Subject'] = sub
        m['From'] = se
        m['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as srv:
            srv.login(se, sp)
            srv.send_message(m)
        print(f"Email successfully sent to {to}")
    except Exception as e:
        print(f"Failed to send email to {to}. Error: {e}")

def get_student_email(rn):
    with open(sf, mode='r') as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            if r['roll_number'] == rn:
                return r['mailid']
    return None

def get_all_students():
    ls = []
    if os.path.exists(sf):
        with open(sf, mode='r') as f:
            rdr = csv.DictReader(f)
            for r in rdr:
                ls.append(r)
    return ls

def add_student():
    rn = input("Enter Roll Number: ")
    nm = input("Enter Name: ")
    mid = input("Enter Email ID: ")
    hst = input("Enter Hostel Name: ")
    
    ls = get_all_students()
    for s in ls:
        if s['roll_number'] == rn:
            print("Student with this roll number already exists!")
            return

    with open(sf, mode='a', newline='') as f:
        w = csv.writer(f)
        w.writerow([rn, nm, mid, hst])
    print("Student added successfully.")

def display_menu():
    c = input("Display menu for (1) Full Week or (2) Specific Day? ")
    if c == '1':
        for d, ms in mu.items():
            print(f"\n--- {d} ---")
            for mt, i in ms.items():
                print(f"{mt}: {i}")
    elif c == '2':
        d = input("Enter day (e.g., Monday): ").capitalize()
        if d in mu:
            print(f"\n--- {d} ---")
            for mt, i in mu[d].items():
                print(f"{mt}: {i}")
        else:
            print("Invalid day.")

def update_menu():
    d = input("Enter day to update (e.g., Monday): ").capitalize()
    if d not in mu:
        print("Invalid day.")
        return
    mt = input("Enter meal type (Breakfast/Lunch/Dinner): ").capitalize()
    if mt not in mu[d]:
        print("Invalid meal type.")
        return
    
    ni = input(f"Enter new item for {d} {mt}: ")
    mu[d][mt] = ni
    print("Menu updated successfully.")

def record_attendance():
    dt = input("Enter date (YYYY-MM-DD): ")
    mt = input("Enter meal type (Breakfast/Lunch/Dinner): ").capitalize()
    
    ex = []
    if os.path.exists(af):
        with open(af, mode='r') as f:
            rdr = csv.DictReader(f)
            ex = list(rdr)
            
    ar = any(r['date'] == dt and r['meal_type'] == mt for r in ex)
    
    if ar:
        c = input("Attendance for this date and meal already exists. Overwrite? (y/n): ")
        if c.lower() != 'y':
            print("Attendance recording cancelled.")
            return
        
        ex = [r for r in ex if not (r['date'] == dt and r['meal_type'] == mt)]
        with open(af, mode='w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['roll_number', 'date', 'meal_type', 'status'])
            w.writeheader()
            w.writerows(ex)

    pr = input("Enter comma-separated roll numbers of present students: ").split(',')
    pr = [x.strip() for x in pr if x.strip()]
    
    ls = get_all_students()
    
    with open(af, mode='a', newline='') as f:
        w = csv.writer(f)
        for s in ls:
            rn = s['roll_number']
            st = 'Present' if rn in pr else 'Absent'
            w.writerow([rn, dt, mt, st])
            
    print("Attendance recorded successfully.")

def log_complaint():
    rn = input("Enter Roll Number: ")
    mid = get_student_email(rn)
    if not mid:
        print("Student not found.")
        return

    dt = datetime.now().strftime("%Y-%m-%d")
    ct = input("Enter complaint details: ")
    cid = f"CMP{int(datetime.now().timestamp())}"
    
    with open(cf, mode='a', newline='') as f:
        w = csv.writer(f)
        w.writerow([cid, rn, dt, ct, 'Open'])
    
    print("Complaint logged locally. Attempting to send email...")
    send_email(mid, "Complaint Registered", f"Your complaint ({cid}) has been logged successfully on {dt}.")

def resolve_complaint():
    cid = input("Enter Complaint ID to resolve: ")
    cs = []
    upd = False
    tr = None
    
    with open(cf, mode='r') as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            if r['complaint_id'] == cid and r['status'] == 'Open':
                r['status'] = 'Resolved'
                tr = r['roll_number']
                upd = True
            cs.append(r)
            
    if upd:
        with open(cf, mode='w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['complaint_id', 'roll_number', 'date', 'complaint_text', 'status'])
            w.writeheader()
            w.writerows(cs)
            
        print("Complaint status updated to Resolved.")
        rm = input("Enter resolution message to send to student: ")
        mid = get_student_email(tr)
        if mid:
            send_email(mid, f"Complaint {cid} Resolved", rm)
    else:
        print("Complaint ID not found or already resolved.")

def display_open_complaints():
    print("\n    Open Complaints   ")
    oc = []
    with open(cf, mode='r') as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            if r['status'] == 'Open':
                oc.append(r)
                
    oc.sort(key=lambda x: x['date'])
    for c in oc:
        print(f"[{c['date']}] ID: {c['complaint_id']} | Roll: {c['roll_number']} | Text: {c['complaint_text']}")

def calculate_student_bill(rn, mo):
    mc = 0
    try:
        with open(af, mode='r') as f:
            rdr = csv.DictReader(f)
            for r in rdr:
                if r['roll_number'] == rn and r['date'].startswith(mo) and r['status'] == 'Present':
                    mc += 1
    except FileNotFoundError:
        pass 
        
    vc = mc * pmr
    tb = bc + vc
    return mc, vc, tb

def generate_student_bill():
    rn = input("Enter Roll Number: ")
    mo = input("Enter Month (YYYY-MM): ")
    se_m = get_student_email(rn)
    
    if not se_m:
        print("Student not found.")
        return

    mc, vc, tb = calculate_student_bill(rn, mo)
    
    bs = (
        f"    Mess Bill Summary for {mo}    \n"
        f"Roll Number: {rn}\n"
        f"Meals Consumed: {mc}\n"
        f"Base Charge: Rs. {bc}\n"
        f"Variable Charge: Rs. {vc}\n"
        f"Total Bill Amount: Rs. {tb}\n"
    )
    print(bs)
    send_email(se_m, f"Mess Bill for {mo}", bs)

def generate_hostel_bills():
    hn = input("Enter Hostel Name: ")
    mo = input("Enter Month (YYYY-MM): ")
    
    fn = f"hostel_bills_{mo}.txt"
    ls = get_all_students()
    
    with open(fn, mode='w') as f:
        f.write(f"Hostel Mess Bills for {hn} - {mo}\n")
        f.write("="*40 + "\n")
        
        for s in ls:
            if s['hostel'].lower() == hn.lower():
                mc, vc, tb = calculate_student_bill(s['roll_number'], mo)
                f.write(f"Roll: {s['roll_number']} | Name: {s['name']} | Total Meals: {mc} | Bill: Rs. {tb}\n")
                
    print(f"Hostel bills generated successfully and saved to {fn}")

def main():
    initialize_files()
    while True:
        print("\n=== Smart Campus Hostel Mess Management System ===")
        print("1. Add New Student")
        print("2. Manage Menu")
        print("3. Record Daily Attendance")
        print("4. Manage Complaints")
        print("5. Generate Monthly Bills")
        print("6. Exit")
        
        c = input("Enter your choice: ")
        
        if c == '1':
            add_student()
        elif c == '2':
            sc = input("(1) Display Menu or (2) Update Menu? ")
            if sc == '1': display_menu()
            elif sc == '2': update_menu()
        elif c == '3':
            record_attendance()
        elif c == '4':
            sc = input("(1) Log Complaint, (2) Resolve Complaint, or (3) View Open Complaints? ")
            if sc == '1': log_complaint()
            elif sc == '2': resolve_complaint()
            elif sc == '3': display_open_complaints()
        elif c == '5':
            sc = input("(1) Individual Student Bill or (2) Full Hostel Bills? ")
            if sc == '1': generate_student_bill()
            elif sc == '2': generate_hostel_bills()
        elif c == '6':
            print("Exiting system. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()