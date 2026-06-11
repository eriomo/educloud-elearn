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

# ---------------------------------------------------------------------------
# Fallback keyword knowledge base.
# This is the SAME data used before. It is now only a SAFETY NET: the engine
# first tries to read keywords from the TopicKeyword table in the database
# (Supabase). If that table is empty or cannot be reached, it falls back to
# this built-in copy so the system never breaks.
# ---------------------------------------------------------------------------
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


def _load_keyword_kb():
    """
    Build the keyword knowledge base used for topic scoring.

    Tries the database (Supabase) first by reading the TopicKeyword table,
    so that topics can be edited from the admin panel without changing code.
    Returns a dict: {topic: [(keyword, weight), ...]}.
    Falls back to the built-in TOPIC_KEYWORDS if the table is empty or any
    error occurs (e.g. during migrations or if the table does not exist yet).
    """
    try:
        # Imported lazily so this module can still be imported before Django
        # apps are ready (for example, during migrations).
        from assessments.models import TopicKeyword
        kb = {}
        rows = TopicKeyword.objects.filter(is_active=True).values_list('topic', 'keyword', 'weight')
        for topic, keyword, weight in rows:
            kb.setdefault(topic, []).append((keyword.lower(), weight or 1))
        if kb:
            return kb
    except Exception:
        # Table missing, DB not ready, or any other issue -> use fallback.
        pass
    # Fallback: weight every built-in keyword as 1.
    return {topic: [(kw.lower(), 1) for kw in kws] for topic, kws in TOPIC_KEYWORDS.items()}


def _score_by_options(opt_a, opt_b, opt_c, opt_d):
    """Strongest signal: the format of the answer options reveals the topic."""
    options = [str(o) for o in [opt_a, opt_b, opt_c, opt_d] if o]
    if not options:
        return None
    joined = ' '.join(options).lower()
    # All options are money -> Commercial Maths
    if all(('n' in o.lower() and re.search(r'n\s*\d', o.lower())) or 'naira' in o.lower() or '\u20a6' in o for o in options):
        return 'Commercial Maths'
    # All options are areas / volumes -> Geometry
    if all(re.search(r'cm2|cm3|m2|m3|cm\u00b2|cm\u00b3', o.lower()) for o in options):
        return 'Geometry'
    # All options have degrees -> Geometry
    if all('degree' in o.lower() or '\u00b0' in o for o in options):
        return 'Geometry'
    # All options are speeds -> Time & Speed
    if all('km/h' in o.lower() or 'km/hr' in o.lower() or 'm/s' in o.lower() for o in options):
        return 'Time & Speed'
    # All options are percentages -> Percentages
    if all('%' in o for o in options):
        return 'Percentages'
    # All options are fractions like 3/4 -> Fractions
    if all(re.search(r'\d+\s*/\s*\d+', o) for o in options):
        return 'Fractions'
    # All options are time units -> Time & Speed
    if all(re.search(r'year|month|week|day|hour|min|sec', o.lower()) for o in options):
        return 'Time & Speed'
    return None


def _score_by_units_symbols(text):
    """Second signal: units and symbols inside the question."""
    if re.search(r'km/h|km/hr|m/s', text):
        return 'Time & Speed'
    if re.search(r'\bcm2\b|\bm2\b|\bcm3\b|\bm3\b|cm\u00b2|cm\u00b3', text):
        return 'Geometry'
    if re.search(r'\d+\s*:\s*\d+', text):           # ratio pattern 3:2
        return 'Ratio & Proportion'
    if re.search(r'\u20a6|\bn\d|naira|kobo', text):  # money
        return 'Commercial Maths'
    if re.search(r'%|percent', text):
        return 'Percentages'
    if re.search(r'\b[xyz]\s*[+\-=]|[+\-=]\s*[xyz]\b', text):  # algebra
        return 'Algebra'
    return None


VERB_OBJECT_PATTERNS = [
    (r'(find|calculate)\s+.*(area|perimeter|volume|circumference|radius|diameter)', 'Geometry'),
    (r'(find|calculate)\s+.*(angle|degrees)', 'Geometry'),
    (r'(find|calculate)\s+.*(mean|mode|median|average|range)', 'Statistics'),
    (r'(find|calculate)\s+.*(profit|loss|interest|discount|commission)', 'Commercial Maths'),
    (r'(percentage|%)\s*(profit|loss|gain)', 'Commercial Maths'),
    (r'(profit|loss|gain|discount|commission|bought|sold|cost price|selling price)', 'Commercial Maths'),
    (r'(how much|what is the cost|find the cost|what is the price)', 'Commercial Maths'),
    (r'(find|calculate)\s+.*(speed|distance)', 'Time & Speed'),
    (r'(how long|what time|when did|at what speed|how far)', 'Time & Speed'),
    (r'(solve|find)\s+.*(value of [xyz]|equation)', 'Algebra'),
    (r'if\s+\d*\s*[xyz]\s*[+\-=]', 'Algebra'),
    (r'(shared|divided|split)\s+.*(ratio|proportion)', 'Ratio & Proportion'),
    (r'in the ratio\s+\d+\s*:\s*\d+', 'Ratio & Proportion'),
    (r'(express|write)\s+.*(figures|words|numeral)', 'Number & Numeration'),
    (r'place value|significant figure|round off|approximate', 'Number & Numeration'),
    (r'(reduce|simplify)\s+.*(lowest|fraction|term)', 'Fractions'),
    (r'(arrange|order)\s+.*(fraction|ascending|descending)', 'Fractions'),
    (r'(find|what is)\s+.*(lcm|hcf|highest common|lowest common)', 'LCM & HCF'),
]


def _score_by_verb_object(text):
    """Third signal: the verb together with what it acts on."""
    for pattern, topic in VERB_OBJECT_PATTERNS:
        if re.search(pattern, text):
            return topic
    return None


def get_topic(question_text, option_a='', option_b='', option_c='', option_d=''):
    """
    Multi-signal topic assignment.

    Combines four weighted signals and returns the highest-scoring topic:
      - answer-option format        (3 points, strongest)
      - units and symbols           (2 points)
      - verb + object pattern       (2 points)
      - keyword knowledge base      (1 point per matching keyword, from Supabase)

    Backwards compatible: still works if called with only the question text.
    """
    text = (question_text or '').lower()
    scores = {}

    def add(topic, pts):
        if topic:
            scores[topic] = scores.get(topic, 0) + pts

    # Signal 1 - answer options (strongest)
    add(_score_by_options(option_a, option_b, option_c, option_d), 3)
    # Signal 2 - units and symbols
    add(_score_by_units_symbols(text), 2)
    # Signal 3 - verb + object
    add(_score_by_verb_object(text), 2)
    # Signal 4 - keyword knowledge base (from the database / Supabase)
    kb = _load_keyword_kb()
    for topic, pairs in kb.items():
        match = sum(weight for kw, weight in pairs if kw in text)
        if match:
            add(topic, match)

    if not scores or max(scores.values()) == 0:
        return 'General Mathematics'
    return max(scores, key=scores.get)


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
    has_fraction = int(bool(re.search(r'[\u215f\u2154\u2157\u00be\u215d\u2158\u215e\u00bd\u2153\u00bc]', question_text)) or '/' in text)

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
