import os
import pickle
import numpy as np
from django.core.management.base import BaseCommand
from assessments.models import CEQuestion
from assessments.ml.features import extract_features, auto_label, get_topic

TRAINING_DATA = [
    ("Express in figures: four million fifty-five thousand eight hundred and sixteen", "4550806", "4505816", "4055816", "4005860", 0),
    ("State the place value of 2 in 354250", "10", "200", "20", "100", 0),
    ("Find the HCF of 6 9 and 12", "3", "5", "7", "2", 0),
    ("How many seconds are there in 8 minutes 12 seconds", "512", "500", "492", "490", 0),
    ("Write three hundred thousand and sixty five in figure", "30000056", "300000065", "3000065", "300065", 0),
    ("What is the place value of 2 in 304.12", "hundredth", "tens", "tenth", "hundreds", 0),
    ("Find the HCF of 48 84 and 88", "4", "2", "12", "21", 0),
    ("Find the LCM of 8 12 and 24", "16", "24", "32", "48", 0),
    ("How many minutes are there in one and three quarter hours", "75 mins", "105 mins", "90 mins", "120 mins", 0),
    ("Find the mean mark 4 5 3 4 5 5 7 6 2 5", "5", "4", "7", "5.6", 0),
    ("How many days are there in 7 weeks", "49 days", "409 days", "28 days", "490 days", 0),
    ("What is the LCM of 4 6 and 10", "70", "56", "45", "60", 0),
    ("What is the sum of angles in a triangle", "180 degrees", "120 degrees", "360 degrees", "90 degrees", 0),
    ("What is the place value of 6 in 268", "6", "600", "60", "680", 0),
    ("Change 240 minutes to hours", "4 hrs", "250 hrs", "12 hrs", "6 hrs", 0),
    ("What is 50 percent of 100kg", "50kg", "25kg", "5.0kg", "100kg", 0),
    ("Find the sum of values of 7 in the numbers 479 and 729", "1400", "6900", "770", "140", 0),
    ("Reduce 9 over 27 to lowest term", "3/9", "3", "6/9", "1/3", 0),
    ("How many seconds make up three and half minutes", "240", "210", "180", "120", 0),
    ("Write in figure twelve thousand seven hundred and two", "12000702", "1200702", "127002", "12702", 0),
    ("What is the place value of 5 in 504.13", "5 hundreds", "5 hundredths", "5 tens", "5 thousands", 0),
    ("Write six million three hundred thousand and nine in figures", "6000309", "6003009", "6030009", "6300009", 0),
    ("How many minutes are there in 660 seconds", "11 minutes", "14 minutes", "15 minutes", "16 minutes", 0),
    ("What is the place value of 2 in 8.217", "Hundreds", "Hundredths", "Tens", "Tenths", 0),
    ("What is the value of 3 in 642.531", "Ten thousands", "Thousand", "Hundredth", "Tenth", 0),
    ("Add 2.6 plus 0.068 plus 1.59", "1.239", "2.258", "2.198", "4.258", 0),
    ("What is the mode of the scores 5 1 3 4 3 4 2 4 4", "4", "2", "3", "5", 0),
    ("Change 15 percent to fraction in its lowest term", "15/100", "15/50", "1/10", "3/20", 0),
    ("What is the HCF of 12 15 and 21", "5", "3", "4", "7", 0),
    ("Find the difference between the LCM and HCF of 16 and 32", "30", "8", "16", "24", 0),
    ("How many seconds are there in 12 hours", "42500", "4500", "43200", "452", 0),
    ("Find the sum of angles at a point", "90 degrees", "180 degrees", "270 degrees", "360 degrees", 0),
    ("Reduce 9 over 27 to its lowest term", "3/9", "1/3", "6/9", "1/9", 0),
    ("How many liters of water are in a tank whose volume is 60000cm3", "60 liters", "6 liters", "600 liters", "6000 liters", 0),
    ("Write the numeral 80050017 in words", "Eight hundred five thousand", "Eight hundred fifty thousand", "Eighty thousand five hundred", "Eighty million fifty thousand", 0),
    ("How much is 12.5 percent of N320", "N20", "N40", "N30", "N60", 1),
    ("A car travels 50km on 8 litres of fuel how far will it travel on 24 litres", "24km", "243km", "271km", "150km", 1),
    ("Calculate the perimeter of the square whose area is 225cm2", "3600cm", "360cm", "240cm", "60cm", 1),
    ("Find the average of 40 64 47 and 33", "33", "42", "46", "47", 1),
    ("The distance from Calabar to Abuja is 4800km if it took 6 hours find average speed", "100km/hr", "900km/hr", "800km/hr", "1000km/hr", 1),
    ("A woman bought beans for N12 and sold for N15 what was her percentage profit", "125%", "80%", "56%", "25%", 1),
    ("Find the area of a circle whose radius is 7cm take pi as 22 over 7", "44cm2", "77cm2", "82cm2", "154cm2", 1),
    ("Calculate the area of a triangle whose height is 8cm and base is 6cm", "32cm2", "28cm2", "24cm2", "12cm2", 1),
    ("Find the speed of a car that travels 3600km in 20 hours", "100km/hr", "120km/hr", "180km/hr", "90km/hr", 1),
    ("A dealer bought a TV set for N15000 and sold it for N18000 find his profit percentage", "10%", "20%", "30%", "40%", 1),
    ("Find the simple interest on N600 for 5 years at 8 percent per annum", "N2.4", "N24.00", "N240.00", "N2400.00", 1),
    ("Calculate the circumference of a circle of radius 3.5cm pi equals 22 over 7", "77cm", "75cm", "44cm", "22cm", 1),
    ("Find the perimeter of a triangle with sides 5cm 7cm and 9cm", "12cm", "14cm", "16cm", "21cm", 1),
    ("A motorist travelled at 72km per hour for 2 and half hours how many km has he covered", "144", "176", "180", "210", 1),
    ("Find the value of x in the equation 36 over x equals 6 over 5", "6", "30", "36", "90", 1),
    ("Express 270 as a product of prime numbers", "2x3x3x3x5", "2x2x3x3x5", "3x3x5x6", "2x3x5x9", 1),
    ("Find the volume of a cylinder with radius 4cm and height 14cm", "704cm3", "532cm3", "337cm3", "176cm3", 1),
    ("A man earned N5000 for 10 days work how much in 14 days", "N12000", "N7000", "N700", "N500", 1),
    ("Find the LCM of 16 32 and 40", "160", "180", "200", "210", 1),
    ("If 8 children ate a crate of egg in 12 days how long will 6 children take", "24 days", "16 days", "12 days", "10 days", 1),
    ("A car travels at 120km per hour how long to travel 160km", "45 mins", "1 and a third hours", "1 and half hours", "2 hrs", 1),
    ("Find the simple interest on N140 invested for one and half years at 8 percent per annum", "N16.08", "N156.80", "N16.80", "N12", 1),
    ("Find the mean of 5 6 6 8 9 and 11", "6.5", "7.5", "7.0", "8.0", 1),
    ("Find the circumference of a circle whose diameter is 21cm take pi as 22 over 7", "32cm", "66cm", "55cm", "44cm", 1),
    ("Find the area of a circle whose diameter is 14cm pi equals 22 over 7", "154cm2", "96cm2", "44cm2", "22cm2", 1),
    ("Find the volume of a cylinder whose radius is 5cm and height 7cm pi equals 22 over 7", "250cm3", "350cm3", "400cm3", "550cm3", 1),
    ("If 9 exercise books cost N63 find cost of one dozen", "17", "27", "63", "84", 1),
    ("Arrange in ascending order two thirds four fifths three quarters", "3/4 2/3 4/5", "2/3 3/4 4/5", "4/5 3/4 2/3", "2/3 4/5 3/4", 1),
    ("Find the distance travelled at 80km per hour for 3 hours", "235km", "240km", "245km", "250km", 1),
    ("Calculate the area of a rectangle whose length is 100cm and breadth is 78cm", "980cm2", "156cm2", "1560cm2", "7800cm2", 1),
    ("Find the perimeter of a circle of radius 7cm take pi as 22 over 7", "154cm", "49cm", "44cm", "22cm", 1),
    ("A farmer shared 60 chickens in ratio 5 to 3 to 2 how many did each person receive", "30 18 and 12", "30 12 and 18", "12 15 and 10", "50 40 and 20", 1),
    ("Find the value of x in x over 60 equals 3 over 4", "15", "13", "3", "45", 1),
    ("A girl walked 7km in 2 hours and 5km in 1 hour what was her average speed", "6km/h", "4.25km/h", "4km/h", "4.75km/h", 1),
    ("Solve the following simultaneous equation x plus y equals 3 and 3x plus y equals 5", "x=1 y=2", "x=4 y=3", "x=1 y=3", "x=2 y=1", 2),
    ("Find the time which will yield simple interest of N1800 in N2400 at 5 percent per annum", "2 and half years", "5 years", "10 years", "15 years", 2),
    ("A rectangle has the following properties except the area equals half base times height", "opposite sides equal", "opposite sides parallel", "area half base height", "adjacent sides perpendicular", 2),
    ("Which of the following is not divisible by 5", "45", "130", "265", "554", 2),
    ("A job takes 28 men 26 days how many men needed to complete it in 14 days", "45 men", "32 men", "52 men", "48 men", 2),
    ("If N450 is shared among three people in ratio 2 to 3 to 4 how much will Joel get", "N140", "N80", "N150", "N200", 2),
    ("Find the rate at which N280 will earn N21 simple interest for two and half years", "5%", "4%", "3%", "3 and half percent", 2),
    ("A discount of 25 percent is allowed on a TV marked N2500 how much will buyer pay", "N500", "N1875", "N2000", "N4000", 2),
    ("Calculate the fourth angle of a quadrilateral with angles 121 35 and 74 degrees", "120 degrees", "230 degrees", "130 degrees", "200 degrees", 2),
    ("Calculate the number of sides of a polygon whose sum of angles is 1800 degrees", "12", "15", "11", "8", 2),
    ("What is the smallest number that can be taken from 3978 to give a number divisible by 46", "35", "31", "22", "43", 2),
    ("Two men shared cost of business in ratio 7 to 19 smaller share is N56000 find total cost", "N54000", "N48000", "N162000", "N156000", 2),
    ("An exporter sold oranges worth N30000 and received 6 percent commission how much did he receive", "N1800", "N23000", "N28800", "N28200", 2),
    ("If 2x plus 8 equals 26 what is x", "18", "36", "16", "9", 2),
    ("Solve 17 plus 2a equals a plus 7", "-10", "-8", "8", "10", 2),
    ("Find the value of x in the equation 5x minus 3 equals 2x plus 12", "-5", "0", "5", "10", 2),
    ("A shopkeeper bought a dozen loaves for N900 and sold each for N71.25 calculate percentage loss", "5%", "6%", "7%", "8%", 2),
    ("Given that x plus 3 equals 12 find square root of x minus 2", "4", "3", "2", "1", 2),
    ("If 2 times p plus 3 equals 18 find the value of p", "2", "4", "6", "8", 2),
    ("Solve for y if y over 3 equals 2 plus y over 5", "6", "10", "15", "30", 2),
    ("A man had taxable income of N1500 paid tax at 4 kobo on each naira how much tax", "N375", "N60", "N620", "N224", 2),
    ("Find the value of t in the equation 3t minus 5 equals t plus 15", "-20", "-10", "5", "10", 2),
    ("Find the value of x in equation 3x plus 1 equals x plus 9", "1", "2", "3", "4", 2),
    ("Three telecom masts flash at intervals of 15 25 and 30 seconds after how many seconds do they flash together", "50", "75", "10", "150", 2),
    ("Express 196 as a product of prime factors in index form", "2 squared times 7 squared", "2 squared times 3 squared", "2 squared times 5 cubed", "2 to power 4 times 3 cubed", 2),
    ("The areas of a parallelogram and rectangle are same rectangle is 10cm by 8cm one side of parallelogram is 16cm find height", "10cm", "80cm", "8cm", "5cm", 2),
    ("If 4x squared minus 3 equals 1 which is a value of 1 minus 2x", "4", "1", "0", "-1", 2),
    ("A discount of 25 percent allowed for television marked N2500 how much will buyer pay", "N500", "N1875", "N2000", "N52000", 2),
    ("Find the rate which N280 will earn N21 simple interest for two and half years", "5%", "4%", "3%", "2 and half percent", 2),
]


class Command(BaseCommand):
    help = 'Train the ML difficulty classifier and classify all questions'

    def handle(self, *args, **kwargs):
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import cross_val_score

        self.stdout.write('Collecting training data...')
        X, y = [], []

        db_questions = list(CEQuestion.objects.all())
        for q in db_questions:
            features = extract_features(
                q.question_text, q.option_a, q.option_b, q.option_c, q.option_d
            )
            label = auto_label(q.question_text)
            X.append(features)
            y.append(label)

        self.stdout.write(f'  Database: {len(db_questions)} questions')

        for item in TRAINING_DATA:
            q_text, opt_a, opt_b, opt_c, opt_d, label = item
            features = extract_features(q_text, opt_a, opt_b, opt_c, opt_d)
            X.append(features)
            y.append(label)

        self.stdout.write(f'  Hardcoded: {len(TRAINING_DATA)} questions')
        self.stdout.write(f'  Total training samples: {len(X)}')

        X = np.array(X)
        y = np.array(y)

        unique, counts = np.unique(y, return_counts=True)
        names = {0: 'Easy', 1: 'Medium', 2: 'Hard'}
        self.stdout.write('Class distribution:')
        for u, c in zip(unique, counts):
            self.stdout.write(f'  {names[int(u)]}: {c}')

        self.stdout.write('Training Random Forest...')
        clf = RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            min_samples_split=2,
            random_state=42,
            class_weight='balanced',
        )

        n_splits = min(5, int(min(counts)))
        if n_splits >= 2:
            cv_scores = cross_val_score(clf, X, y, cv=n_splits, scoring='accuracy')
            self.stdout.write(
                f'Cross-validation accuracy: {cv_scores.mean():.1%} (+/- {cv_scores.std():.1%})'
            )

        clf.fit(X, y)

        feature_names = [
            'word_count', 'avg_word_length', 'has_negative', 'bloom_score',
            'num_operations', 'option_avg_length', 'has_numbers', 'has_fraction',
            'complexity', 'has_algebra', 'has_multi_step', 'option_is_numeric',
        ]
        self.stdout.write('Feature importances:')
        for name, imp in sorted(
            zip(feature_names, clf.feature_importances_), key=lambda x: -x[1]
        ):
            bar = 'X' * int(imp * 30)
            self.stdout.write(f'  {name:<20} {bar} {imp:.3f}')

        model_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'ml', 'model.pkl'
        )
        model_path = os.path.abspath(model_path)
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        with open(model_path, 'wb') as f:
            pickle.dump(clf, f)
        self.stdout.write(self.style.SUCCESS(f'Model saved to {model_path}'))

        self.stdout.write('Classifying all existing CE questions...')
        classified = 0
        for q in CEQuestion.objects.all():
            features = extract_features(
                q.question_text, q.option_a, q.option_b, q.option_c, q.option_d
            )
            pred = clf.predict(np.array([features]))[0]
            q.difficulty_predicted = {0: 'easy', 1: 'medium', 2: 'hard'}[int(pred)]
            q.topic = get_topic(q.question_text)
            q.save()
            classified += 1

        self.stdout.write(self.style.SUCCESS(f'Done! Classified {classified} CE questions.'))
