from django.core.management.base import BaseCommand
from assessments.models import CEQuestion
from lessons.models import Subject


QUESTIONS = [
    # Year 2014
    ("Express in figures: four million, fifty-five thousand, eight hundred and sixteen", "4,550,806", "4,505,816", "4,055,816", "4,005,860", "C", 2014),
    ("State the place value of 2 in 354250.", "10", "200", "20", "100", "C", 2014),
    ("Find the HCF of 6, 9 and 12.", "3", "5", "7", "2", "A", 2014),
    ("Approximate 0.008062 to 3 significant figures.", "0.008062", "0.0081", "0.00806", "0.0080", "C", 2014),
    ("How much is 12.5% of N320.00?", "N20", "N40", "N30", "N60", "B", 2014),
    ("Express 270 as a product of prime numbers.", "2x3x3x3x5", "2x2x3x3x5", "3x3x5x6", "2x3x5x9", "A", 2014),
    ("A car travels 50km on 8 litres of fuel. How far will it travel on 24 litres?", "24km", "243km", "271km", "150km", "D", 2014),
    ("Hemense is 23 years old. Five years ago, he was twice as old as Doose. How old will Doose be in 5 years time?", "19 years", "38 years", "24 years", "28 years", "A", 2014),
    ("What is the product of 0.40 and 6.003 correct to 3 decimal places?", "2.40", "0.240", "0.24", "0.024", "B", 2014),
    ("A boy arrived at school at 8.15am. If he stayed in school for 4hrs 20 minutes, when did he leave?", "11.15am", "12.05pm", "12.35pm", "1.15pm", "C", 2014),
    ("Mallam Abdul shared 72 mangoes between Eze and Femi such that Femi took 6 more than Eze. What is Eze's share?", "42", "30", "36", "28", "B", 2014),
    ("A clock shows 1.10pm and is 20 minutes fast. What is the correct time?", "11.50am", "12.00noon", "12.10pm", "12.50pm", "D", 2014),
    ("Calculate the perimeter of the square whose area is 225cm2.", "3600cm", "360cm", "240cm", "60cm", "D", 2014),
    ("Arrange in ascending order: 2/3, 4/5, 3/4.", "3/4, 2/3, 4/5", "2/3, 3/4, 4/5", "4/5, 3/4, 2/3", "2/3, 4/5, 3/4", "B", 2014),
    ("A ladder is placed against a wall 4m high and the base 3m from the wall. What is the length of the ladder?", "16m", "12m", "9m", "5m", "D", 2014),
    ("The distance from Calabar to Abuja is 4800km. If it took an aeroplane 6hrs, find the average speed.", "100km/hr", "900km/hr", "800km/hr", "1000km/hr", "C", 2014),
    ("A woman bought a measure of beans for N12 and sold it for N15, what was her percentage profit?", "125%", "80%", "56%", "25%", "D", 2014),
    ("Reduce 225/300 to its lowest form.", "2/3", "3/5", "3/4", "7/9", "C", 2014),
    ("Two men shared the cost of a business in the ratio 7:19. If the smaller share is N56,000, find the total cost.", "N54,000", "N48,000", "N162,000", "N156,000", "C", 2014),
    ("A woman bought a measure of beans for N12 and sold it for N15. What was her percentage profit?", "125%", "80%", "56%", "25%", "D", 2014),
    ("An exporter sold oranges worth N30,000 and received a 6% commission. How much did he receive?", "N1,800", "N23,000", "N28,800", "N28,200", "A", 2014),
    ("A job takes 28 men 26 days to complete. How many men are needed to complete it in 14 days?", "45 men", "32 men", "52 men", "48 men", "C", 2014),
    ("Solve the simultaneous equation: x+y = 3, 3x+y = 5.", "x=1,y=2", "x=4,y=3", "x=1,y=3", "x=2,y=1", "A", 2014),
    ("If N450.00 is shared among Samson, Joel and Ibrahim in the ratio 2:3:4, how much will Joel get?", "N140.00", "N80.00", "N150.00", "N200.00", "C", 2014),
    ("Find the time which will yield simple interest of N1,800 in N2,400 at 5% per annum.", "2 and half years", "5 years", "10 years", "15 years", "D", 2014),

    # Year 2015
    ("Find the sum of the values of 7 in the numbers 479 and 729.", "1400", "6900", "770", "140", "C", 2015),
    ("Reduce 9/27 to lowest term.", "3/9", "3", "6/9", "1/3", "D", 2015),
    ("A bag of cement costs N1,400. What is the cost of 36 bags?", "N36,000", "N14,460", "N36,400", "N50,400", "D", 2015),
    ("Change 2/3 to two decimal places.", "0.67", "0.20", "1.066", "2.10", "A", 2015),
    ("A farmer shared 60 chickens in ratio 5:3:2, how many did each person receive?", "30, 18 and 12", "30, 12 and 18", "12, 15 and 10", "18, 30 and 12", "A", 2015),
    ("Three chickens of same weight cost N1,470. Find the cost of seven chickens.", "N470", "N1,049", "N3,430", "N6,400", "C", 2015),
    ("Find the area of the triangle below. Height 1.68cm, base 3.36cm.", "1.68cm2", "3.36cm2", "1.9cm2", "33.6cm2", "A", 2015),
    ("What is the simple interest on N140 invested for 1 and half years at 8% per annum?", "N16.08", "N156.80", "N16.80", "N12", "C", 2015),
    ("A dealer bought a TV set for N15,000 and sold it for N18,000. Find his profit percentage.", "10%", "20%", "30%", "40%", "B", 2015),
    ("Express 96 in index form.", "2 cubed x 3 x 5", "2 cubed x 5 cubed", "2 to the 5 x 3", "2 to the 5 x 5", "C", 2015),
    ("Find the value of x in x/60 = 3/4.", "15", "13", "3", "45", "D", 2015),
    ("A girl walked 7km in 2 hours and 5km in 1 hour. What was her average speed?", "6km/h", "4.25km/h", "4km/h", "4.75km/h", "C", 2015),
    ("An aeroplane leaves Lagos for Yola at 12:15pm, taking 1 hour 20 minutes. When does it arrive?", "1.35pm", "2.35pm", "12.35pm", "4.35pm", "A", 2015),
    ("Find the LCM and HCF difference of 16 and 32.", "30", "8", "16", "24", "C", 2015),
    ("If 6 boys can do a piece of work in 4 days, how long will 8 boys take?", "4 days", "8 days", "2 days", "3 days", "D", 2015),
    ("The average of three numbers is 16. Two of the numbers are 20 and 24. What is the third?", "4", "22", "18", "10", "A", 2015),
    ("If 2x + 8 = 26, what is x?", "18", "36", "16", "9", "C", 2015),
    ("What is the volume of a cylinder with radius 5cm and height 7cm? pi = 22/7.", "250cm3", "350cm3", "400cm3", "550cm3", "B", 2015),
    ("How many litres of water are in a tank with volume 60,000cm3?", "60 liters", "6 liters", "600 liters", "6000 liters", "A", 2015),

    # Year 2016
    ("Write the figure 40,050,000 in words.", "Forty thousand and fifty", "Four million fifty thousand", "Forty million and fifty", "Forty million and five thousand", "C", 2016),
    ("State the place value of 7 in 83017264.", "Thousands", "Tens", "Millions", "Hundreds", "A", 2016),
    ("Find the HCF of 60, 63 and 72.", "20", "3", "7", "8", "B", 2016),
    ("Find the LCM of 5, 10 and 30.", "12", "26", "24", "30", "D", 2016),
    ("Three telecom masts flash at intervals of 15, 25 and 30 seconds. After how many seconds do they flash together?", "50 sec", "75 sec", "10 sec", "150 sec", "D", 2016),
    ("A car travels at 120km per hour. How long to travel 160km?", "45 mins", "1 and 1/3 hrs", "1 and half hrs", "2 hrs", "B", 2016),
    ("Evaluate: 9 and 3/8 + 10 and 5/8.", "20", "19 and 5/8", "19 and 3/8", "20 and 3/8", "A", 2016),
    ("Express 60cm as a percentage of 3m.", "60%", "40%", "20%", "30%", "C", 2016),
    ("Mrs. Arop has 835 rolls of lace at N864 each. How much did she realise?", "N721.00", "N7,214.00", "N721,440.00", "N721,404.00", "C", 2016),
    ("If the area of a square is 196cm2, find its perimeter.", "14cm", "56cm", "22cm", "24cm", "B", 2016),
    ("There are 15 bags each with 48 sweets. Shared equally among 36 bags. How many per bag?", "15", "12", "20", "25", "C", 2016),
    ("A ladder against a building 20m above ground. Foot is 15m away. What is length of ladder?", "25m", "15m", "18m", "20m", "A", 2016),
    ("Find the perimeter of a triangle with sides 3cm, 4cm and 5cm.", "6cm", "18cm", "12cm", "10cm", "C", 2016),
    ("Calculate area of rectangle with length 100cm and breadth 78cm.", "980cm2", "156cm2", "1560cm2", "7800cm2", "D", 2016),
    ("A car on a journey at 80km/h for 2 hours then 50km/h for 2 hours. Find total distance.", "260km", "160km", "100km", "360km", "A", 2016),
    ("A horse runs 162.5km in 2 and half hours. What is its speed?", "62km/h", "65km/h", "55km/h", "52km/h", "B", 2016),
    ("Calculate the fourth angle of quadrilateral with angles 121, 35 and 74 degrees.", "120 degrees", "230 degrees", "130 degrees", "200 degrees", "C", 2016),
    ("Calculate the number of sides of a polygon whose sum of angles is 1800 degrees.", "12", "15", "11", "8", "A", 2016),
    ("When x = 9, what is the value of 3x - 5?", "2", "12", "6", "22", "D", 2016),
    ("Find the average of 40, 64, 47 and 33.", "47", "46", "33", "42", "D", 2016),
    ("Find the square root of 2 and 1/4.", "1/6", "1/3", "1 and 3/4", "3/2", "D", 2016),

    # Year 2017
    ("What is the value of 3 in 642.531?", "Tens", "Hundreds", "Tenth", "Hundredth", "D", 2017),
    ("Find the HCF of 24 and 32.", "4", "8", "12", "16", "B", 2017),
    ("Round off 0.0376 to 2 significant figures.", "0.1", "0.03", "0.037", "0.038", "D", 2017),
    ("Simplify: 2 and half + 1 and quarter + 1 and 3/8.", "3 and half", "4 and 1/8", "5 and 1/8", "3 and 4/5", "B", 2017),
    ("What percentage of 500 is 25?", "5%", "10%", "15/100", "25%", "A", 2017),
    ("There are 572 students, 5/11 are boys. How many are girls?", "312 girls", "320 girls", "310 girls", "300 girls", "A", 2017),
    ("There are 80 million people, 44% are women. How many men? Give to nearest whole number.", "45 million", "44 million", "43 million", "42 million", "A", 2017),
    ("A bus used 5 hours 20 minutes from Kaduna to Makurdi arriving at 1.30pm. When did it leave?", "11.20am", "9.20pm", "8.10am", "9.10am", "D", 2017),
    ("Audu scored 8 out of 20 marks in a test. What percentage did he score?", "8%", "20%", "28%", "40%", "D", 2017),
    ("Find the square root of 4900.", "70", "10", "17", "7", "A", 2017),
    ("Manjo's salary of N500 per annum increased by 15%. What is his new salary?", "N425", "N515", "N575", "N315", "C", 2017),
    ("What is the product of 89.73 and 0.0010?", "0.08973", "8973", "879.3", "0.879", "A", 2017),
    ("If N450.00 is shared in ratio 2:3:4, how much will Joel get?", "N140.00", "N80.00", "N150.00", "N180.00", "C", 2017),
    ("A circular pond has diameter 28m. What is its area? pi = 22/7.", "42cm2", "616 cm2", "88 cm2", "44 cm2", "B", 2017),
    ("Find the speed of a car that travels 3600km in 20 hrs.", "100km/hr", "120km/hr", "180km/hr", "90km/hr", "C", 2017),
    ("If 2y + 3 = 5. What is the value of y?", "1", "4", "3", "2", "A", 2017),
    ("If the number of HIV cases in 2005 was 250,000 and in 2006 was 180,000, what is percentage decrease?", "28%", "38%", "48%", "18%", "A", 2017),
    ("A discount of 25% is allowed on a TV marked N2,500. How much will buyer pay?", "N500", "N1,875", "N2,000", "N4,000", "B", 2017),
    ("If 54 oranges cost N360, find the cost of 3 oranges.", "N20", "N120", "N180", "N125", "A", 2017),
    ("Given numbers 5,1,3,4,3,4,2,4,4. Find the mean.", "4", "5", "3 and 1/3", "3", "C", 2017),
    ("Given numbers 5,1,3,4,3,4,2,4,4. Find the median.", "4", "3", "2", "1", "A", 2017),
    ("Given numbers 5,1,3,4,3,4,2,4,4. Find the mode.", "4", "2", "3", "5", "A", 2017),
    ("Given numbers 5,1,3,4,3,4,2,4,4. Find the range.", "2", "4", "3", "5", "B", 2017),

    # Year 2018
    ("How many seconds are there in 8 minutes 12 seconds?", "512 seconds", "500 seconds", "492 seconds", "490 seconds", "C", 2018),
    ("There are 750 students. If 70% are girls, how many are boys?", "225", "310", "490", "525", "A", 2018),
    ("The ratio of length to breadth of a room is 7:5. Find length if breadth is 10m.", "10m", "12m", "14m", "21m", "C", 2018),
    ("Increase 80 by 10%.", "8", "10", "80", "88", "D", 2018),
    ("Odiri bought 12 cartons of biscuit for N3,000. Find cost of 7 cartons.", "N250", "N442", "N840", "N1,750", "D", 2018),
    ("Find the simple interest on N600 for 5 years at 8% per annum.", "N2.4", "N24.00", "N240.00", "N2400.00", "C", 2018),
    ("If 8 children ate a crate of egg in 12 days, how long will 6 children take?", "24 days", "16 days", "12 days", "10 days", "B", 2018),
    ("Find the LCM of 12 and 18.", "4", "8", "18", "36", "C", 2018),
    ("Find the sum of HCF and LCM of 8 and 12.", "4", "6", "20", "28", "C", 2018),
    ("Find the value of x in the equation: 3x + 1 = x + 9.", "1", "2", "3", "4", "D", 2018),
    ("Find the area of a circle with radius 7cm. pi = 22/7.", "44cm2", "77cm2", "82cm2", "154cm2", "D", 2018),
    ("Calculate area of triangle with height 8cm and base 6cm.", "32cm2", "28cm2", "24cm2", "12cm2", "C", 2018),
    ("A square has how many lines of symmetry?", "4", "3", "2", "1", "A", 2018),
    ("The average of 6, 10, X, 20 and 30 is 18. What is x?", "90", "66", "24", "14", "C", 2018),
    ("Find the value of t in the equation 3t - 5 = t + 15.", "-20", "-10", "5", "10", "D", 2018),
    ("Find the value of x in equation: 5x - 3 = 2x + 12.", "-5", "0", "5", "15", "C", 2018),
    ("Find the perimeter of a circle of radius 7cm. pi = 22/7.", "154cm", "49cm", "44cm", "14cm", "C", 2018),
    ("A car uses 10 litres of fuel for 40km. What distance will 25 litres cover?", "60km", "70km", "80km", "100km", "D", 2018),
    ("The perimeter of a square is 28cm. Find its area.", "284cm2", "784cm2", "144cm2", "49cm2", "D", 2018),
    ("A circular pond has diameter 28cm. What is its area? pi = 22/7.", "42cm2", "616cm2", "88cm2", "34cm2", "B", 2018),
    ("At what speed does a man walk to cover 12km in 3 hours?", "36km/h", "4km/h", "6km/h", "2km/h", "B", 2018),
    ("4y + 7 = 55, what is the value of y?", "12", "48", "14", "6", "C", 2018),
    ("Given numbers 5,1,3,4,3,2,4,4,10. Find the mode.", "4", "2", "3", "6", "A", 2018),
    ("Given numbers 5,1,3,4,3,2,4,4,10. Find the range.", "2", "4", "3", "9", "D", 2018),

    # Year 2019
    ("How many seconds make up 3 and half minutes?", "240", "210", "180", "120", "B", 2019),
    ("Write in figure: Twelve thousand, seven hundred and two.", "12000702", "1200702", "127002", "12702", "D", 2019),
    ("Nike deposits N5000 at 5% per annum for 2 years. How much is the simple interest?", "N20", "N50", "N100", "N500", "D", 2019),
    ("Chuks bought five books at N40 each and sold them for N150. What is the loss?", "N50", "N45", "N40", "N5", "A", 2019),
    ("Festus bought shoes for N5,000 and sold for N4,000. What is his percentage loss?", "10", "20", "30", "40", "B", 2019),
    ("In a class, there are 30 girls and 45 boys. Find ratio of girls to boys.", "1:3", "2:3", "3:1", "3:2", "B", 2019),
    ("One-fourth of a number is 5. Find the number.", "10", "15", "20", "25", "C", 2019),
    ("A worker earns N4,000 per month. How much in half a year?", "N48,000", "N32,400", "N24,000", "N8,000", "C", 2019),
    ("What is the cost of 60 oranges if 4 cost N20?", "N480", "N400", "N300", "N48", "C", 2019),
    ("What is the place value of 5 in 504.13?", "5 hundreds", "5 hundredths", "5 tens", "5 thousands", "A", 2019),
    ("The difference of two numbers is 60. If smaller number is 90, what is their sum?", "300", "240", "230", "150", "B", 2019),
    ("A motorist travelled at 72km/h for 2 and half hours. How many km covered?", "144", "176", "180", "210", "C", 2019),
    ("Amaka is 20 years old and her sister is x years younger. How old is sister?", "x2 years", "20x years", "20/x years", "(20-x) years", "D", 2019),
    ("An aeroplane at 245km/h for 2 hours. What is the distance?", "166km", "360km", "490km", "560km", "C", 2019),
    ("Find the volume of a cylinder with radius 4cm and height 14cm.", "704cm2", "532cm2", "337cm2", "176cm2", "A", 2019),
    ("Solve: 17 + 2a = a + 7.", "-10", "-8", "8", "10", "A", 2019),
    ("Find the perimeter of a triangle with sides 5cm, 7cm and 9cm.", "12cm", "14cm", "16cm", "21cm", "D", 2019),
    ("What is the mode of the score: 1, 3, 2, 3, 5?", "0", "1", "2", "3", "D", 2019),
    ("Find the average of: 3, 2, 6, 1, 3.", "5", "4", "3", "1", "C", 2019),
    ("If the area of a square is 36cm2 find the perimeter.", "36cm", "24cm", "12cm", "6cm", "B", 2019),
    ("The longest side of a right-angled triangle is known as?", "adjacent", "diagonal", "hypotenuse", "opposite", "C", 2019),

    # Year 2020
    ("Write six million, three hundred thousand and nine in figures.", "6,000,309", "6,003,009", "6,030,009", "6,300,009", "D", 2020),
    ("How many minutes are there in 660 seconds?", "11 minutes", "14 minutes", "15 minutes", "16 minutes", "A", 2020),
    ("What is the place value of 2 in 8.217?", "Hundreds", "Hundredths", "Tens", "Tenths", "D", 2020),
    ("Convert 12.4865 to 3 decimal places.", "12.480", "12.486", "12.487", "12.500", "C", 2020),
    ("Amaka and Amina shared N2,800. Amaka gets thrice Amina's share. How much did Amina get?", "N2100", "N1300", "N950", "N700", "D", 2020),
    ("A man bought 500 oranges and gave out 30% of them. How many does he have left?", "150", "350", "400", "650", "B", 2020),
    ("Which of the following is not a factor of 60?", "6", "8", "12", "30", "B", 2020),
    ("Find the LCM of 16, 32, and 40.", "160", "180", "200", "300", "A", 2020),
    ("A boy divides 54 by y and the result is 6. Find the value of y.", "3", "9", "23", "60", "B", 2020),
    ("Which of the following is not a perfect square?", "36", "49", "70", "81", "C", 2020),
    ("If a number multiplies itself to give 289, what is the number?", "11", "12", "13", "17", "E", 2020),
    ("Find the value of x-3, if 14+x=20.", "28", "21", "7", "3", "D", 2020),
    ("The volume of a cube is 64cm. Find the length.", "3cm", "4cm", "5cm", "6cm", "B", 2020),
    ("If 2x-18 = 0, find the value of x.", "0", "1", "2", "9", "D", 2020),
    ("Find the volume of a cylinder of radius 2cm and height 14cm. pi = 22/7.", "120cm3", "136cm3", "142cm3", "176cm3", "D", 2020),
    ("If the area of a rectangle is 24cm2 and the length is 8cm, find the breadth.", "16cm", "12cm", "10cm", "3cm", "D", 2020),
    ("Find the area of a circle whose diameter is 14cm. pi = 22/7.", "154cm2", "96cm2", "44cm2", "22cm2", "A", 2020),
    ("The area of a rectangle is 60cm2. Length is 5cm. Find the breadth.", "65cm", "25cm", "15cm", "12cm", "D", 2020),
    ("Calculate the circumference of a circle of radius 3.5cm. pi = 22/7.", "77cm", "75cm", "44cm", "22cm", "C", 2020),
    ("Find the average of: 1, 3, 5, 7, 9, 11.", "5", "6", "7", "9", "B", 2020),
    ("Find the mode of: 4, 3, 7, 5, 3, 6, 7, 3.", "7", "6", "5", "3", "D", 2020),
    ("Solve for y, if y/3 = 2 + y/5.", "6", "10", "15", "30", "C", 2020),
]


class Command(BaseCommand):
    help = 'Load sample Mathematics questions into the database'

    def handle(self, *args, **kwargs):
        subject, created = Subject.objects.get_or_create(
            name='Mathematics',
            defaults={
                'class_level': 6,
                'color': '#2B6B8A',
            }
        )
        if created:
            self.stdout.write(f'Created subject: Mathematics')
        else:
            self.stdout.write(f'Subject already exists: Mathematics')

        added = 0
        skipped = 0

        for q_text, opt_a, opt_b, opt_c, opt_d, correct, year in QUESTIONS:
            if CEQuestion.objects.filter(question_text=q_text, exam_year=year).exists():
                skipped += 1
                continue

            # Auto classify using ML if available
            difficulty = 'medium'
            topic = 'General Mathematics'
            try:
                from assessments.ml.classifier import predict_difficulty, predict_topic
                difficulty = predict_difficulty(q_text, opt_a, opt_b, opt_c, opt_d)
                topic = predict_topic(q_text)
            except Exception:
                from assessments.ml.features import auto_label, get_topic
                label = auto_label(q_text)
                difficulty = {0: 'easy', 1: 'medium', 2: 'hard'}[label]
                topic = get_topic(q_text)

            CEQuestion.objects.create(
                subject=subject,
                exam_year=year,
                question_text=q_text,
                option_a=opt_a,
                option_b=opt_b,
                option_c=opt_c,
                option_d=opt_d,
                correct_option=correct if correct in ['A', 'B', 'C', 'D'] else 'A',
                difficulty_level=difficulty,
                difficulty_predicted=difficulty,
                topic=topic,
            )
            added += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done! Added {added} questions. Skipped {skipped} duplicates.'
        ))
