import streamlit as st
import random
import itertools
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt

VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
SUITS = ['h', 'd', 'c', 's']

SUIT_SYMBOLS = {
    'h': '♥️',
    'd': '♦️',
    'c': '♣️',
    's': '♠️',
}

VALUE_DISPLAY = {
    'T': '10',
    'J': 'J',
    'Q': 'Q',
    'K': 'K',
    'A': 'A',
    '2': '2',
    '3': '3',
    '4': '4',
    '5': '5',
    '6': '6',
    '7': '7',
    '8': '8',
    '9': '9',
}

def create_deck():
    return [v + s for v in VALUES for s in SUITS]

def parse_hand(hand_str):
    if not hand_str:
        return []
    return hand_str.strip().split()

def validate_hand(hand):
    for card in hand:
        if len(card) != 2:
            return False, f"Invalid card: {card}. Cards should be 2 characters like 'Ah'."
        
        value, suit = card[0].upper(), card[1].lower()
        if value not in VALUES:
            return False, f"Invalid value in card: {card}. First character should be one of {', '.join(VALUES)}."
        if suit not in SUITS:
            return False, f"Invalid suit in card: {card}. Second character should be one of {', '.join(SUITS)}."
    
    normalized_hand = [c[0].upper() + c[1].lower() for c in hand]
    
    if len(normalized_hand) != len(set(normalized_hand)):
        return False, "Duplicate cards detected."
    
    return True, ""

def normalize_card(card):
    return card[0].upper() + card[1].lower()

def card_to_html(card):
    card = normalize_card(card)
    value, suit = card[0], card[1]
    
    display_value = VALUE_DISPLAY[value]
    suit_symbol = SUIT_SYMBOLS[suit]
    
    color = "red" if suit in ['h', 'd'] else "black"
    
    return f'<span style="color:{color}; font-weight:bold; font-size:1.2em;">{display_value}{suit_symbol}</span>'

def cards_to_html(cards):
    return " ".join(card_to_html(card) for card in cards)

def get_card_value(card):
    return VALUES.index(card[0].upper())

def get_hand_rank(hand):
    if len(hand) != 5:
        return (0, [])
    
    normalized_hand = [normalize_card(card) for card in hand]
    
    values = [card[0] for card in normalized_hand]
    suits = [card[1] for card in normalized_hand]
    
    value_counts = Counter(values)
    most_common = value_counts.most_common()
    
    is_flush = len(set(suits)) == 1
    
    value_indices = sorted([VALUES.index(v) for v in values])
    is_straight = (value_indices == list(range(min(value_indices), max(value_indices) + 1)))
    
    if set(values) == set(['A', '2', '3', '4', '5']):
        is_straight = True
        value_indices = [0, 1, 2, 3, 12]
    
    if is_straight and is_flush:
        return (9, value_indices)
    elif most_common[0][1] == 4:
        return (8, [VALUES.index(most_common[0][0]), VALUES.index(most_common[1][0])])
    elif most_common[0][1] == 3 and most_common[1][1] == 2:
        return (7, [VALUES.index(most_common[0][0]), VALUES.index(most_common[1][0])])
    elif is_flush:
        return (6, sorted([VALUES.index(v) for v in values], reverse=True))
    elif is_straight:
        return (5, value_indices)
    elif most_common[0][1] == 3:
        return (4, [VALUES.index(most_common[0][0])] + sorted([VALUES.index(v) for v, c in most_common[1:]], reverse=True))
    elif most_common[0][1] == 2 and most_common[1][1] == 2:
        high_pair = VALUES.index(most_common[0][0])
        low_pair = VALUES.index(most_common[1][0])
        kicker = VALUES.index(most_common[2][0])
        return (3, [max(high_pair, low_pair), min(high_pair, low_pair), kicker])
    elif most_common[0][1] == 2:
        return (2, [VALUES.index(most_common[0][0])] + sorted([VALUES.index(v) for v, c in most_common[1:]], reverse=True))
    else:
        return (1, sorted([VALUES.index(v) for v in values], reverse=True))

def hand_name(rank):
    names = {
        9: "Straight Flush",
        8: "Four of a Kind",
        7: "Full House",
        6: "Flush",
        5: "Straight",
        4: "Three of a Kind",
        3: "Two Pair",
        2: "One Pair",
        1: "High Card",
        0: "Invalid Hand"
    }
    return names.get(rank, "Unknown")

def get_best_hand(cards):
    if len(cards) < 5:
        return None, (0, [])
    
    possible_hands = list(itertools.combinations(cards, 5))
    best_hand = max(possible_hands, key=lambda h: get_hand_rank(list(h)))
    best_rank = get_hand_rank(list(best_hand))
    
    return list(best_hand), best_rank

def compare_hands(hand1_rank, hand2_rank):
    if hand1_rank[0] > hand2_rank[0]:
        return 1
    elif hand1_rank[0] < hand2_rank[0]:
        return -1
    
    for tb1, tb2 in zip(hand1_rank[1], hand2_rank[1]):
        if tb1 > tb2:
            return 1
        elif tb1 < tb2:
            return -1
    
    return 0

def find_outs(player_hand, community_cards, all_known_cards):
    player_hand = [normalize_card(card) for card in player_hand]
    community_cards = [normalize_card(card) for card in community_cards]
    all_known_cards = [normalize_card(card) for card in all_known_cards]
    
    current_cards = player_hand + community_cards
    current_best_hand, current_rank = get_best_hand(current_cards)
    
    deck = [card for card in create_deck() if card not in all_known_cards]
    
    outs = {}
    
    for card in deck:
        new_community = community_cards + [card]
        new_cards = player_hand + new_community
        
        new_best_hand, new_rank = get_best_hand(new_cards)
        
        if compare_hands(new_rank, current_rank) > 0:
            hand_type = hand_name(new_rank[0])
            if hand_type not in outs:
                outs[hand_type] = []
            outs[hand_type].append(card)
    
    return outs

def monte_carlo_winner_probability(player_hands, community_cards, iterations=10000):
    normalized_player_hands = [[normalize_card(card) for card in hand] for hand in player_hands]
    normalized_community = [normalize_card(card) for card in community_cards]
    
    all_known_cards = [card for hand in normalized_player_hands for card in hand] + normalized_community
    deck = [card for card in create_deck() if card not in all_known_cards]
    
    community_needed = 5 - len(normalized_community)
    
    wins = [0] * len(player_hands)
    ties = 0
    
    for _ in range(iterations):
        if community_needed > 0:
            random_community = random.sample(deck, community_needed)
            complete_community = normalized_community + random_community
        else:
            complete_community = normalized_community
        
        best_hands = []
        for hand in normalized_player_hands:
            player_cards = hand + complete_community
            best_hand, rank = get_best_hand(player_cards)
            best_hands.append((best_hand, rank))
        
        winners = []
        best_rank = (0, [])
        
        for i, (hand, rank) in enumerate(best_hands):
            comparison = compare_hands(rank, best_rank)
            if comparison > 0:
                winners = [i]
                best_rank = rank
            elif comparison == 0:
                winners.append(i)
        
        if len(winners) == 1:
            wins[winners[0]] += 1
        else:
            ties += 1
    
    win_probabilities = [w / iterations for w in wins]
    tie_probability = ties / iterations
    
    return win_probabilities, tie_probability

def main():
    st.set_page_config(page_title="Poker Probability Calculator", layout="wide")
    
    st.title("Multi-Player Poker Probability Calculator")
    
    st.markdown("""
    Calculate the probability of each player winning given their hole cards and community cards.
    
    **Card Format Examples**: `Ah` (Ace of hearts), `2s` (2 of spades), `Tc` (10 of clubs), `Kd` (King of diamonds)
    """)
    
    num_players = st.number_input("Number of players:", min_value=2, max_value=10, value=2, step=1)
    
    player_hands = []
    valid_hands = []
    
    col1, col2 = st.columns(2)
    
    with col1:
        for i in range(0, num_players, 2):
            if i < num_players:
                hand_str = st.text_input(f"Player {i+1}'s hand (e.g., 'Ah Ks'):", key=f"player_{i}")
                hand = parse_hand(hand_str)
                
                valid, error = validate_hand(hand)
                if hand and not valid:
                    st.error(f"Player {i+1}'s hand: {error}")
                    valid_hands.append(False)
                else:
                    valid_hands.append(True)
                
                player_hands.append(hand)
    
    with col2:
        for i in range(1, num_players, 2):
            if i < num_players:
                hand_str = st.text_input(f"Player {i+1}'s hand (e.g., 'Ah Ks'):", key=f"player_{i}")
                hand = parse_hand(hand_str)
                
                valid, error = validate_hand(hand)
                if hand and not valid:
                    st.error(f"Player {i+1}'s hand: {error}")
                    valid_hands.append(False)
                else:
                    valid_hands.append(True)
                
                player_hands.append(hand)
    
    community_cards_str = st.text_input("Enter community cards (optional):", "")
    community_cards = parse_hand(community_cards_str)
    
    valid_community, community_error = validate_hand(community_cards)
    if community_cards and not valid_community:
        st.error(f"Invalid community cards: {community_error}")
    
    if all(valid_hands) and (not community_cards or valid_community):
        all_cards = [normalize_card(card) for hand in player_hands for card in hand] + [normalize_card(card) for card in community_cards]
        if len(all_cards) != len(set(all_cards)):
            st.error("Duplicate cards detected across players or community cards.")
        else:
            st.subheader("Current Cards")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Player Cards:**")
                for i, hand in enumerate(player_hands):
                    if hand:
                        normalized_hand = [normalize_card(card) for card in hand]
                        st.markdown(f"Player {i+1}: {cards_to_html(normalized_hand)}", unsafe_allow_html=True)
            
            with col2:
                st.write("**Community Cards:**")
                if community_cards:
                    normalized_community = [normalize_card(card) for card in community_cards]
                    st.markdown(f"{cards_to_html(normalized_community)}", unsafe_allow_html=True)
                else:
                    st.write("None")
            
            iterations = st.number_input("Number of simulations:", min_value=1000, max_value=1000000, value=10000, step=1000)
            
            if st.button("Calculate Winning Probabilities"):
                if any(len(hand) == 0 for hand in player_hands):
                    st.error("Each player must have at least one card.")
                else:
                    with st.spinner("Running simulation..."):
                        win_probs, tie_prob = monte_carlo_winner_probability(
                            player_hands, community_cards, iterations
                        )
                    
                    st.subheader("Win Probabilities")
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    labels = [f"Player {i+1}" for i in range(num_players)] + ["Tie"]
                    sizes = win_probs + [tie_prob]
                    colors = plt.cm.tab10(range(len(sizes)))
                    
                    wedges, texts, autotexts = ax.pie(
                        sizes, 
                        labels=labels, 
                        colors=colors,
                        autopct='%1.1f%%',
                        startangle=90,
                        pctdistance=0.85
                    )
                    
                    ax.axis('equal')
                    plt.setp(autotexts, size=10, weight="bold")
                    plt.setp(texts, size=12)
                    
                    st.pyplot(fig)
                    
                    for i, prob in enumerate(win_probs):
                        st.write(f"Player {i+1}: {prob:.4f} ({prob*100:.2f}%)")
                    st.write(f"Tie: {tie_prob:.4f} ({tie_prob*100:.2f}%)")
                    
                    st.subheader("Player Outs")
                    
                    all_known_cards = [card for hand in player_hands for card in hand] + community_cards
                    
                    for i, hand in enumerate(player_hands):
                        if hand:
                            st.write(f"**Player {i+1} Outs:**")
                            
                            player_outs = find_outs(hand, community_cards, all_known_cards)
                            
                            if player_outs:
                                for hand_type, outs in player_outs.items():
                                    st.markdown(f"For {hand_type} ({len(outs)} cards): {cards_to_html(outs)}", unsafe_allow_html=True)
                            else:
                                st.write("No outs found.")
                            
                            st.write("---")
                    
                    if community_cards:
                        st.subheader("Current Best Hands")
                        for i, hand in enumerate(player_hands):
                            if hand:
                                normalized_hand = [normalize_card(card) for card in hand]
                                normalized_community = [normalize_card(card) for card in community_cards]
                                
                                best_hand, best_rank = get_best_hand(normalized_hand + normalized_community)
                                if best_hand:
                                    st.markdown(f"Player {i+1}: {hand_name(best_rank[0])} - {cards_to_html(best_hand)}", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
