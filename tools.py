import cv2
from math import sqrt

def calc_distance(p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2
    return round(sqrt((x1-x2)**2 + (y1-y2)**2))

def run_all_methods(image, template, verbose=False):
    methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
               'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
    images = []
    maps = []

    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).copy()
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY).copy()

    for meth in methods:
        img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).copy()
        method = eval(meth)
        # Apply template Matching
        e1 = cv2.getTickCount()

        res = cv2.matchTemplate(img, template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        e2 = cv2.getTickCount()
        time = (e2 - e1) / cv2.getTickFrequency()
        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc
        bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])
        cv2.rectangle(img, top_left, bottom_right, 255, 2)

        cv2.putText(img, str(time), (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    2, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(img, str(meth), (200, 200), cv2.FONT_HERSHEY_SIMPLEX,
                    2, (255, 0, 0), 2, cv2.LINE_AA)

        if verbose:
            print(f'Method: {meth}, time: {time}')

        maps.append(res)
        images.append(img)

    return images, methods, maps


def run_sqdiff(image, template, verbose=False):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).copy()

    if len(template.shape) == 3:
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY).copy()

    e1 = cv2.getTickCount()

    res = cv2.matchTemplate(image, template, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    e2 = cv2.getTickCount()
    time = (e2 - e1) / cv2.getTickFrequency()

    top_left = min_loc
    bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])

    if verbose:
        print(f'time: {time}')

    return top_left, bottom_right


def run_ccoeff_normed(image, template, verbose=False):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).copy()

    if len(template.shape) == 3:
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY).copy()

    e1 = cv2.getTickCount()

    res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    e2 = cv2.getTickCount()
    time = (e2 - e1) / cv2.getTickFrequency()

    top_left = max_loc
    bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])

    if verbose:
        print(f'time: {time}')

    return top_left, bottom_right


def calculate_distance(,width=960, height=540)