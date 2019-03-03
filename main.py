import sys
import math
import time
from collections import OrderedDict
from pprint import pprint

input_file = sys.argv[1]
TAG_INDEX = -1

def read_photos(input_file):
    global n_lines
    n_lines = int(input_file.readline())
    photos = {}
    horizontals = {}
    verticals = {}
    for i in range(n_lines):
        l = input_file.readline().strip().split(' ')
        tags = set(l[2:])
        photo = (i, l[0], len(tags), tags)
        photos[i] = photo
        if photo[1] == 'H':
            horizontals[i] = photo
        else:
            verticals[i] = photo
    return photos, horizontals, verticals

def find_vertical(candidates):
    return next(iter(candidates))

def combine_verticals(verticals):
    ordered_vs = OrderedDict()
    for v in sorted(verticals, key=lambda v: verticals[v][2], reverse=True):
        ordered_vs[v] = verticals[v]
    slides = {}
    tag_index = {}
    while len(ordered_vs) > 0:
        current = next(iter(ordered_vs))
        current_p = verticals[current]
        del ordered_vs[current]
        other = find_vertical(ordered_vs)
        other_p = verticals[other]
        del ordered_vs[other]
        tags = current_p[TAG_INDEX] | other_p[TAG_INDEX]
        slide_id = (current, other)
        slides[slide_id] = (len(tags), tags)
        for t in tags:
            if t in tag_index:
                tag_index[t].add(slide_id)
            else:
                tag_index[t] = {slide_id,}
    return slides, tag_index

def photos_to_slides(photos, horizontals, verticals):
    slides, tag_index = combine_verticals(verticals)
    for _, p in horizontals.items():
        if p[1] == 'H':
            s_id = (p[0],)
            n_tags = p[2]
            tags = p[3]
        slides[s_id] = (n_tags, tags)
        for t in tags:
            if t in tag_index:
                tag_index[t].add(s_id)
            else:
                tag_index[t] = {s_id,}
    return slides, tag_index

def score(s1, s2):
    t1 = s1[TAG_INDEX]
    t2 = s2[TAG_INDEX]
    return min([
        len(t1 & t2),
        len(t1 - t2),
        len(t2 - t1)]
    )

def next_greedy(slide, slide_id, slides, candidates):
    highest = None
    highest_score = -1
    highest_n_tags = 0
    for i, c_id in enumerate(candidates):
        c_slide = slides[c_id]
        c_score = score(slide, c_slide)
        if c_score > highest_score:
            highest = c_id
            highest_score = c_score
            highest_n_tags = c_slide[0]
        elif c_score == highest_score and c_slide[0] > highest_n_tags:
            highest = c_id
            highest_score = c_score
            highest_n_tags = c_slide[0]
    return highest, highest_score

def all_greedy(slides, tag_index):
    # TODO: grow in two directions
    total_score = 0
    # all slides that have not been added are a candidate
    global_candidates = set(slides.keys())
    # initialize slideshow with slide with most tags
    first = next(iter(slides))
    slideshow = [first]
    global_candidates.remove(first)
    while(len(global_candidates) > 0):
        current_id = slideshow[-1]
        current_slide = slides[current_id]
        current_tags = current_slide[TAG_INDEX]
        # Remove from slides OrderedDict
        del slides[current_id]
        # Construct set of all slides that have overlapping tags with the current slide
        candidates_by_tags = set()
        for t in current_tags:
            candidates_by_tags |= tag_index[t]
        # Candidates should have overlapping tags and should not be in slideshow yet
        local_candidates = global_candidates & candidates_by_tags
        # Find the slide that yields the highest score (greedily)
        next_slide, score_i = next_greedy(current_slide, current_id, slides, local_candidates)
        if next_slide is not None:
            # A slide was found, append it and remove it from the candidate list
            slideshow.append(next_slide)
            global_candidates.remove(next_slide)
            total_score += score_i
        else:
            found = False
            slide_iterator = iter(slides)
            while not found:
                top_slide = next(slide_iterator)
                found = top_slide in global_candidates
            global_candidates.remove(top_slide)
            slideshow.append(top_slide)
    return slideshow, total_score
def print_slide(slide):
    print(' '.join(map(str, slide)))

def get_score(slideshow, slides):
    tot_score = 0
    ss_len = len(slideshow)
    for i, s in enumerate(slideshow):
        s1 = slides[s]
        if i == ss_len-1:
            continue
        s2 = slides[slideshow[i+1]]
        tot_score += score(s1, s2)
    return tot_score

with open(input_file, 'r') as f:
    # Read all fotos
    photos, horizontals, verticals = read_photos(f)
    slides, tag_index = photos_to_slides(photos, horizontals, verticals)
    print('#slides: {}'.format(len(slides)), file=sys.stderr)
    # Order slides
    ordered_slides = OrderedDict()
    for s in sorted(slides, key=lambda s: slides[s][0], reverse=True):
        ordered_slides[s] = slides[s]
    # Greedily grow slideshow starting with slide with most tags
    slideshow, total_score = all_greedy(ordered_slides, tag_index)
    print('total_score: {} \t len_slideshow: {} '.format(total_score, len(slideshow)), file=sys.stderr)
    print(get_score(slideshow, slides), file=sys.stderr)
    print(len(slideshow))
    for s in slideshow:
        print_slide(s)
        pass
