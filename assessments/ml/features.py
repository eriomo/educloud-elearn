import re

BLOOM_EASY_KEYWORDS = [
    'what is', 'write the', 'state the', 'how many', 'express in figures',
    'write in words', 'place value', 'write in figure', 'find the hcf',
    'find the lcm', 'list', 'define', 'name the', 'express in words',
    'write the numeral', 'how much is', 'what are', 'how long',
    'what time', 'identify', 'write all', 'find the sum',
    'find the difference', 'find the product', 'reduce to', 'lowest term',
    'change to', 'convert to', 'write in figures', 'write six',
    'write three', 'write two', 'how many seconds', 'how many minutes',
    'how many days', 'how many hours',
]

BLOOM_MEDIUM_KEYWORDS = [
    'calculate', 'simplify', 'find the value', 'arrange in',
    'find the area', 'find the perimeter', 'find the speed',
    'find the distance', 'ratio of', 'find the average', 'find the mean',
    'find the mode', 'find the median', 'approximate', 'correct to',
    'round off', 'express as', 'percentage of', 'what percentage',
    'shared among', 'shared between', 'find the cost', 'find the time',
    'find the height', 'find the width', 'find the length',
    'find the angle', 'find the volume', 'find the circumference',
    'find the radius', 'find the diameter', 'solve the equation',
    'find the value of x', 'find the value of y', 'find the weight',
    'find the profit', 'find the loss', 'find the interest',
    'what is the cost', 'how far', 'what is the ratio',
    'find the square root', 'find the cube root',
]

BLOOM_HARD_KEYWORDS = [
    'except', 'simultaneous equation', 'evaluate', 'use this information',
    'simple interest', 'inequalit', 'find the rate', 'product of prime',
    'index form', 'ascending order', 'descending order',
    'which is not', 'profit percent', 'loss percent', 'discount',
    'commission', 'pythagoras', 'hypotenuse', 'parallelogram', 'trapezium',
    'not a factor', 'not divisible', 'which of the following is not',
    'does not belong', 'not true', 'not correct', 'percentage loss',
    'percentage profit', 'percentage gain', 'percentage decrease',
    'percentage increase', 'taxable', 'tax rate', 'exchange rate',
    'shared in the ratio', 'find the total cost', 'how many men',
    'how many women', 'inverse proportion', 'direct proportion',
]

TOPIC_KEYWORDS = {
    'Number & Numeration': [
        'figures', 'words', 'place value', 'numeral', 'digit', 'million',
        'billion', 'thousand', 'hundred', 'roman', 'base', 'significant',
        'decimal places', 'round off', 'approximate', 'prime number',
        'factor', 'multiple', 'index', 'product of prime', 'express in',
    ],
    'Fractions': [
        'fraction', 'numerator', 'denominator', 'mixed', 'improper',
        'simplest form', 'lowest term', 'common', '/', 'simplify',
    ],
    'Decimals': [
        'decimal', '0.', 'tenths', 'hundredths', 'thousandths',
        'decimal places', 'correct to', 'significant figures',
    ],
    'Percentages': [
        'percent', '%', 'percentage',
    ],
    'Ratio & Proportion': [
        'ratio', 'proportion', 'shared', 'divided among', 'in the ratio',
        'rate', 'scale', 'shared among', 'shared between',
    ],
    'Commercial Maths': [
        'simple interest', 'principal', 'per annum', 'interest rate',
        'invested', 'bank', 'savings', 'profit', 'loss', 'discount',
        'commission', 'cost price', 'selling price', 'tax', 'salary',
        'earn', 'bought', 'sold', 'price', 'naira', 'kobo',
    ],
    'Algebra': [
        'equation', 'solve', 'value of x', 'value of y', 'simultaneous',
        'expression', 'simplify', 'inequality', 'algebraic', 'substitut',
        'if x =', 'if y =', 'find x', 'find y',
    ],
    'Geometry': [
        'area', 'perimeter', 'volume', 'angle', 'triangle', 'rectangle',
        'square', 'circle', 'radius', 'diameter', 'circumference',
        'cylinder', 'cube', 'polygon', 'parallel', 'perpendicular',
        'hypotenuse', 'pythagoras', 'trapezium', 'parallelogram',
        'degrees', 'symmetry', 'chord', 'sector', 'arc', 'shape',
    ],
    'Statistics': [
        'mean', 'mode', 'median', 'average', 'range', 'frequency',
        'table', 'graph', 'chart', 'data', 'scores', 'marks',
    ],
    'Time & Speed': [
        'speed', 'distance', 'time', 'km/h', 'hours', 'minutes',
        'seconds', 'clock', 'am', 'pm', 'journey', 'travel', 'fast',
    ],
    'LCM & HCF': [
        'lcm', 'hcf', 'highest common factor', 'lowest common multiple',
        'common factor', 'common multiple',
    ],
}


def get_topic(question_text):
    text = question_text.lower()
    scores = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        scores[topic] = score
    best_topic = max(scores, key=scores.get)
    return best_topic if scores[best_topic] > 0 else 'General Mathematics'


def auto_label(question_text):
    text = question_text.lower()
    if any(kw in text for kw in BLOOM_HARD_KEYWORDS):
        return 2  # Hard
    elif any(kw in text for kw in BLOOM_MEDIUM_KEYWORDS):
        return 1  # Medium
    else:
        return 0  # Easy


def extract_features(question_text, option_a='', option_b='', option_c='', option_d=''):
    text = question_text.lower()
    words = text.split()

    word_count = len(words)
    avg_word_length = sum(len(w) for w in words) / max(len(words), 1)

    negative_words = ['not', 'except', 'false', 'incorrect', 'wrong', 'never', 'cannot', 'does not']
    has_negative = int(any(neg in text for neg in negative_words))

    bloom_score = 0
    if any(kw in text for kw in BLOOM_HARD_KEYWORDS):
        bloom_score = 2
    elif any(kw in text for kw in BLOOM_MEDIUM_KEYWORDS):
        bloom_score = 1

    math_ops = ['calculate', 'find', 'solve', 'simplify', 'evaluate', 'compute', 'determine', 'express']
    num_operations = sum(1 for op in math_ops if op in text)

    options = [str(o) for o in [option_a, option_b, option_c, option_d] if o]
    option_avg_length = sum(len(o) for o in options) / max(len(options), 1)

    has_numbers = int(bool(re.search(r'\d', text)))
    has_fraction = int(bool(re.search(r'[⅟⅔⅗¾⅝⅘⅞½⅓¼]', question_text)) or '/' in text)

    if word_count > 40:
        complexity = 2
    elif word_count > 20:
        complexity = 1
    else:
        complexity = 0

    has_algebra = int(
        bool(re.search(r'\b[xyzpqn]\b', text)) and
        any(op in text for op in ['=', 'find', 'solve', 'value'])
    )

    multi_step_words = ['then', 'after', 'also', 'and then', 'hence', 'therefore']
    has_multi_step = int(any(w in text for w in multi_step_words))

    option_is_numeric = int(all(
        bool(re.search(r'\d', str(o))) for o in [option_a, option_b, option_c] if o
    ))

    return [
        word_count, avg_word_length, has_negative, bloom_score,
        num_operations, option_avg_length, has_numbers, has_fraction,
        complexity, has_algebra, has_multi_step, option_is_numeric,
    ]
