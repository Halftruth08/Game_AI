#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 21:10:18 2018

@author: aarontallman
"""
import os

# import io

import numpy as np
import pandas

LOCAL = os.path.dirname(os.path.dirname(__file__))
CDNM = LOCAL + "/data/wordslist.txt"
debug = False


def cpu_player_1deep(model, clue, board, bonus_guess, verbose=True):
    """if models are identical for codemaster and player, there should be no mistakes
    """
    if verbose is True:
        print("AI player thinking...")
    # guessword = cpu_player_1deep(player_model, clueword, gamegrid, cluenumber-guess)
    perhaps = model[0][model[2][clue]]
    options = {}
    for word in board.values.ravel():
        if word in ["RED", "BLUE", "GREY", "BLACK"]:
            continue
        if model[2][word] in perhaps.keys():
            options[perhaps[model[2][word]]] = word
    topchoices = list(options.keys())
    if len(topchoices) == 0:
        print("No obvious choices... passing turn")
        return "pass"
    if verbose is True:
        # topchoices=list(options.keys())
        topchoices.sort(reverse=True)
        top_choice_report = "Top Choices for %s\n" % clue
        for i in range(min(len(topchoices), 10)):
            top_choice_report += "Choice %i: %s %f \n" % (
                i,
                options[topchoices[i]],
                topchoices[i],
            )
        print(top_choice_report)
    pos = np.argwhere(board.values == options[max(topchoices)]).flatten()
    if bonus_guess > -1:
        passback = "%i,%i" % (pos[0], pos[1])
    else:
        passback = "pass"
    return passback

    # raise IOError


def codemaster(model, player="human", player_model=None):
    """
    """
    if player_model is None:
        player_model = model  # for testing the IO and debugging code
    #!!! BEGIN MAIN
    coloc = model[0]
    # rd = model[1]
    dc = model[2]
    weights = {"red": 1.0, "grey": -0.5, "blue": -1.0, "black": -5.0}
    # redweight={'red':1.0}#how much weight do we give to
    # avoiding the chance of mistakes, based on cost of the mistake
    # PRIME TARGET FOR DEEP Q LEARNING

    gameboard = game_maker()
    gamegrid = layout(gameboard)
    print(gamegrid)  # so we can consider while the computer thinks
    gamenumbers = {}
    for key in gameboard.keys():
        temp = []
        for item in gameboard[key]:
            temp.append(dc.get(item, 0))
        gamenumbers[key] = temp
    cols = get_col_names(gamenumbers)

    likelihoods = get_clues_array(
        gamenumbers["red"],
        gamenumbers["blue"],
        gamenumbers["grey"],
        gamenumbers["black"],
        coloc,
    )
    likes_out = pandas.DataFrame(likelihoods["out"]).transpose()
    likes_in = pandas.DataFrame(likelihoods["in"]).transpose()
    likesbase = pandas.concat([likes_out, likes_in], axis=1)
    likesbase.columns = cols
    # now, all necessary information is stored as a dataframe
    remaining = {}

    for key in gameboard:
        remaining[key] = [1 for i in gameboard[key]]
        # for each answer/turn, redo from here on.
    #    for each turn:
    #    honest = filter_out_cheat_clues(likesbase.index, remaining, gameboard, model)

    while sum(remaining["red"]) > 0:
        clueword, cluenumber = play_turn(
            cols, likesbase, weights, remaining, gameboard, model
        )

        likesbase.drop(model[2][clueword], inplace=True)  # no reusing clues
        for guess in range(1, cluenumber + 2):
            if player == "human":
                guessword = prompt_user(
                    clueword, cluenumber, guess, gameboard, gamegrid
                )
            elif player.find("cpu") > -1:
                guessword = prompt_cpu(
                    player_model, clueword, cluenumber, guess, gameboard, gamegrid
                )
            if guessword == "":
                color = ""
                break
            else:
                color, remaining, likesbase = enact_guess(
                    guessword, remaining, gamegrid, gameboard, likesbase
                )
                if not color == "red":

                    break
        if color == "black":
            print("You've been assassinated!\nGAME OVER")
            break
        if sum(remaining["blue"]) == 0:
            print("The Blue Team Defeated You...\nGAME OVER")
            break
        print(gamegrid)
    if sum(remaining["red"]) == 0:
        print("Congratulations, You've Won!")
        print(gamegrid)
    return gamegrid, gameboard


def get_clues_array(targets, blue, grey, black, coloc):
    """will run once per game, returning the needed data
    to calculate clue strength as a function of what
    words remain on the board.
    out refers to collocations going outwards from a codename
    in as in collocations coming back inwards to a codename.
    think: "codename-centric" terminology
    """
    clue_likelihoods = {"out": {}, "in": {}}
    temp = []
    for target in targets:
        temp.extend(list(coloc[target].keys()))
    temp.sort()
    candidates = [temp[0]]
    for i in range(1, len(temp)):
        if not temp[i] == temp[i - 1]:
            candidates.append(temp[i])

    # 2*targets+1 for odds, 1 for counterweights
    n_metrics = len(targets) + len(grey) + len(blue) + len(black)
    for candidate in candidates:
        clue_likelihoods["out"][candidate] = [0.0 for i in range(n_metrics)]
        clue_likelihoods["in"][candidate] = [0.0 for i in range(n_metrics)]
    for candidate in candidates:
        for i2 in range(len(targets)):
            clue_likelihoods["out"][candidate][i2] += coloc[targets[i2]].get(
                candidate, 0.0
            )
            clue_likelihoods["in"][candidate][i2] += coloc[candidate].get(
                targets[i2], 0.0
            )
        temp = len(targets)
        for i2 in range(len(blue)):
            clue_likelihoods["out"][candidate][i2 + temp] += coloc[blue[i2]].get(
                candidate, 0.0
            )
            clue_likelihoods["in"][candidate][i2 + temp] += coloc[candidate].get(
                blue[i2], 0.0
            )
        temp += len(blue)
        for i2 in range(len(grey)):
            clue_likelihoods["out"][candidate][i2 + temp] += coloc[grey[i2]].get(
                candidate, 0.0
            )
            clue_likelihoods["in"][candidate][i2 + temp] += coloc[candidate].get(
                grey[i2], 0.0
            )
        temp += len(grey)
        for i2 in range(len(black)):
            clue_likelihoods["out"][candidate][i2 + temp] += coloc[black[i2]].get(
                candidate, 0.0
            )
            clue_likelihoods["in"][candidate][i2 + temp] += coloc[candidate].get(
                black[i2], 0.0
            )
    return clue_likelihoods


def get_col_names(gamenumbers):  # uses gamenumbers defined in codemaster
    cols = []
    directions = ["out", "in"]
    for direction in directions:
        for key in gamenumbers.keys():
            for i in range(len(gamenumbers[key])):
                cols.append("%s%i_%s" % (key, i, direction))
    return cols


# uses gameboard & candidates defined in codemaster
def filter_out_cheat_clues(candidates, remaining, gameboard, model):
    honest = []

    def onboard(a):
        if int(a) == 0:
            return False
        else:
            for key in gameboard.keys():
                for i in range(len(gameboard[key])):
                    if remaining[key][i] == 1:
                        if any(
                            [
                                gameboard[key][i].find(model[1][a]) > -1,
                                model[1][a].find(gameboard[key][i]) > -1,
                                model[1][a].find(" ") > -1,
                                model[1][a].find("(") > -1,
                            ]
                        ):
                            return False
            return True

    honest = list(filter(onboard, candidates))

    return honest


def enact_guess(word, remaining, gamegrid, gameboard, likesbase):
    for key in gameboard.keys():
        try:
            colf = np.array(gameboard[key]).tolist().index(word)
            color = key
            break
        except ValueError:
            continue
    try:
        _ = color
    except:
        print("errant guess passed in:", word)
    remaining[color][colf] = 0
    for direction in ["in", "out"]:
        likesbase["%s%i_%s" % (color, colf, direction)] = 0.0
    for i in range(5):
        for i2 in range(5):
            if gamegrid.loc[i, i2] == word:
                gamegrid.loc[i, i2] = color.swapcase()
                break
    return color, remaining, likesbase


def play_turn(cols, likesbase, weights, remaining, gameboard, model):
    honest = filter_out_cheat_clues(likesbase.index, remaining, gameboard, model)
    likes = likesbase.loc[lambda a: honest]
    print("Considering %i options..." % len(likes.index))
    all_in = {}
    all_out = {}
    for key in weights.keys():
        all_in[key] = list(
            filter(lambda a: all([a.find(key) > -1, a.find("in") > -1]), likes.columns)
        )
        all_out[key] = list(
            filter(lambda a: all([a.find(key) > -1, a.find("out") > -1]), likes.columns)
        )
    likes["all_i_sum"] = 0.0
    likes["all_o_sum"] = 0.0
    for key in weights.keys():
        temp1 = key + "s_i_sum"
        temp2 = key + "s_o_sum"
        likes[temp1], likes[temp2] = 0.0, 0.0
        for coln in range(len(all_in[key])):
            if remaining[key][coln] == 1:
                # *weights[key]
                likes["all_i_sum"] += likes[all_in[key][coln]]
                # *weights[key]
                likes["all_o_sum"] += likes[all_out[key][coln]]
                likes[temp1] += likes[all_in[key][coln]]  # *weights[key]
                likes[temp2] += likes[all_out[key][coln]]  # *weights[key]
                # this is total likelihood of bad outcomes per candidate
    # STRATEGY 1: find max in prob codenames, calc odds, take max odds
    # clues

    all_clues = len(likes.index)
    blind_odds = sum(
        [sum(remaining[key]) * weights[key] for key in weights.keys()]
    ) / sum([sum(remaining[key]) for key in weights.keys()])
    n_remaining = float(sum([sum(remaining[key]) for key in weights.keys()]))
    temp = list(filter(lambda a: all([a.find("red") > -1, a.find("in") > -1]), cols))
    top_x, top_i, top_o, top_io, top_oo, red_inl = [], [], [], [], [], []
    newdex = likes.index.tolist()
    filt = []
    for i in likes.index:
        temp2 = likes.loc[i, temp[0] : temp[len(temp) - 1]].nlargest(
            n=sum(remaining["red"])
        )
        if sum(temp2) == 0:
            newdex.remove(i)
            likesbase.drop(i, inplace=True)
            filt.append(False)
            continue
        filt.append(True)
        top_x.append(temp2.index.tolist())
        top_i.append(temp2.get_values())
        temp3 = list(map(lambda a: a.replace("in", "out"), temp2.index.tolist()))
        temp4, temp5, temp6 = [], [], []
        for i2 in temp2.get_values():
            temp6.append(i2 / (likes.at[i, "all_i_sum"]))
        top_io.append(temp6)
        for i2 in temp3:
            temp4.append(likes.at[i, i2])
            temp5.append(likes.at[i, i2] / (likes.at[i, "all_o_sum"]))
        top_o.append(temp4)
        top_oo.append(temp5)
        # red_inl.append(temp2.values)
    likes["filt"] = pandas.Series(filt, index=likes.index)
    likes = likes.loc[lambda a: filt]
    likes["in_max"] = pandas.Series(top_i, index=newdex)
    likes["in_max_idx"] = pandas.Series(top_x, index=newdex)
    likes["out_max"] = pandas.Series(top_o, index=newdex)
    likes["in_odds"] = pandas.Series(top_io, index=newdex)
    likes["out_odds"] = pandas.Series(top_oo, index=newdex)
    # likes['list_redin'] =pandas.Series(red_inl)

    # ev_list = {1: [], 2: [], 3: [], 4: []}
    # optional: rewrite the below function to operate along a column
    ign_ev = {1: [], 2: [], 3: [], 4: []}
    for i in likes.index:
        itotl = likes.at[i, "all_i_sum"]
        temp1i, temp2i, temp3i, temp4i = odds_simulated_guessing(
            i,
            model,
            gameboard,
            likes,
            weights,
            blind_odds,
            n_remaining,
            max_ign=0.4,
            min_ign=0,
        )
        # max_ign = 0.4  # 40% chance words are unknown to other player at max vocab
        # min_ign = 0e4
        # make this tunable
        # ign_ev=temp*(1-ign) + ign * blind_odds
        ign_ev[1].append(temp1i)
        ign_ev[2].append(temp2i)
        ign_ev[3].append(temp3i)
        ign_ev[4].append(temp4i)

    # ev_list = pandas.DataFrame(ev_list, index=likes.index)
    ign_ev = pandas.DataFrame(ign_ev, index=likes.index)

    clue1 = ign_ev.nlargest(1, 1).index[0]
    clue2 = ign_ev.nlargest(1, 2).index[0]
    clue3 = ign_ev.nlargest(1, 3).index[0]
    if debug == True:
        print(model[1][clue1], likes.loc[clue1])
    if debug:
        print("Clue expected value", ign_ev.nlargest(1, 3), "\n")
    if ign_ev.at[clue2, 2] > ign_ev.at[clue1, 1]:
        if ign_ev.at[clue3, 3] > ign_ev.at[clue2, 2]:
            cluenumber = 3
            clueword = model[1][clue3]

        else:
            cluenumber = 2
            clueword = model[1][clue2]
    else:
        cluenumber = 1
        clueword = model[1][clue1]
    return clueword, cluenumber


def prompt_user(clue, number, guessnumber, gameboard, gamegrid):
    codename = ""
    guess = input(
        "%s %i\n%s\n\nGuess(%i/%i) row,column or pass:"
        % (clue, number, gamegrid, guessnumber, number + 1)
    )
    if guess.find(",") > -1:
        a, b = guess.split(",")
        a = int(a)
        b = int(b)
        codename = gamegrid.at[a, b]
        print("Guessing: %s" % codename)
        return codename
    elif guess == "pass":
        print("Passing Turn")
    elif guess == "quit":
        codename = gameboard["black"][0]
    else:
        print("incorrect entry, passing turn as a default while in dev")
    return


def prompt_cpu(player_model, clue, number, guessnumber, gameboard, gamegrid):
    codename = ""
    print(
        "%s %i\n%s\n\nGuess(%i/%i) row,column or pass:"
        % (clue, number, gamegrid, guessnumber, number + 1)
    )

    guess = cpu_player_1deep(player_model, clue, gamegrid, number - guessnumber)
    if guess.find(",") > -1:
        a, b = guess.split(",")
        a = int(a)
        b = int(b)
        codename = gamegrid.at[a, b]
        print("Guessing: %s" % codename)
    elif guess == "pass":
        print("Passing Turn")
    elif guess == "quit":
        codename = gameboard["black"][0]
    else:
        print("incorrect entry, passing turn as a default while in dev")
    return codename


def odds_simulated_guessing(
    cluei,
    model,
    gameboard,
    likes,
    weights,
    blind_odds,
    n_remaining,
    max_ign=0.4,
    min_ign=0,
):
    i = cluei
    itotl = likes.at[i, "all_i_sum"]
    ign = max_ign * (i / len(model[1])) + min_ign
    temp1 = 0.0
    for key in gameboard.keys():
        temp = key + "s_i_sum"
        temp1 += likes.at[i, temp] * weights[key]
    # temp1 = temp1 / itotl
    temp1i = temp1 / itotl * (1.0 - ign) + blind_odds * ign
    temp2i = 0.0
    temp3i = 0.0
    temp4i = 0.0
    templist = likes.at[i, "in_odds"]
    if temp1 > 0.0 and np.count_nonzero(likes["in_max"][i]) > 1:
        for i2 in range(len(templist)):
            l2 = templist[i2]
            l2i = templist[i2] * (1.0 - ign) + ign / n_remaining

            temp0i = (l2i) * (
                (itotl * temp1 - templist[i2] * weights["red"])
                * (1.0 - ign)
                / (itotl - templist[i2])
                + ign
                * (n_remaining * blind_odds - weights["red"])
                / (n_remaining - 1.0)
            )
            temp2i += temp0i
            if np.count_nonzero(likes["in_max"][i]) > 2:
                for i3 in range(len(templist)):
                    if not i2 == i3:
                        l3 = l2 * templist[i3] / (1.0 - templist[i2] / itotl)
                        l3i = l2i * (
                            templist[i3] * itotl / (itotl - templist[i2]) * (1.0 - ign)
                            + ign / (n_remaining - 1.0)
                        )
                        temp00i = l3i * (
                            (
                                itotl * temp1
                                - (templist[i2] + templist[i3]) * weights["red"]
                            )
                            / (itotl - (templist[i2] + templist[i3]))
                            * (1.0 - ign)
                            + ign
                            * (
                                (n_remaining * blind_odds - 2.0 * weights["red"])
                                / (n_remaining - 2.0)
                            )
                        )
                        temp3i += temp00i
                        if np.count_nonzero(likes["in_max"][i]) > 3:
                            for i4 in range(len(templist)):
                                if not i4 == i2 and not i4 == i3:
                                    l4i = l3i * (
                                        templist[i4]
                                        * itotl
                                        / (itotl - (templist[i2] + templist[i3]))
                                        * (1.0 - ign)
                                        + ign / (n_remaining - 2.0)
                                    )
                                    temp000i = l4i * (
                                        (
                                            itotl * temp1
                                            - (
                                                templist[i2]
                                                + templist[i3]
                                                + templist[i4]
                                            )
                                            * weights["red"]
                                        )
                                        / (
                                            itotl
                                            - (
                                                templist[i2]
                                                + templist[i3]
                                                + templist[i4]
                                            )
                                        )
                                        * (1.0 - ign)
                                        + ign
                                        * (
                                            (
                                                n_remaining * blind_odds
                                                - 3.0 * weights["red"]
                                            )
                                            / (n_remaining - 3.0)
                                        )
                                    )
                                    temp4i += temp000i

    #    raise IOError
    temp2i = temp2i + temp1i
    temp3i += temp2i
    temp4i += temp3i
    return temp1i, temp2i, temp3i, temp4i


def game_maker():
    """returns a dict with the words from targets
    split into 4 lists:
        red (9)-- red team's codenames
        blue (8)-- blue team's codenames
        grey (7)-- bystanders
        black (1)-- assassin
    for the sake of simplicity,
    red will always go first.
    the number of words in each list are shown in the above parenthesis
    """
    gameboard = {}
    tr = open(CDNM, "r")  # targets
    targets = tr.read().split("\n")
    tr.close()
    board = np.random.choice(targets, 25, replace=False)
    gameboard["red"] = board[0:9]  # len=9
    gameboard["blue"] = board[9:17]  # len=8
    gameboard["grey"] = board[17:24]  # len=7
    gameboard["black"] = [board[24]]  # len=1

    return gameboard


def layout(gameboard):
    import pandas

    gamegrid = pandas.DataFrame([[""] * 5 for i in range(5)])
    codenames = []
    for value in gameboard.values():
        codenames.extend(value)
    np.random.shuffle(codenames)
    for i1 in range(5):
        for i2 in range(5):
            gamegrid.loc[i1, i2] = codenames.pop()

    return gamegrid
