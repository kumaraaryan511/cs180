@app.route('/api/value', methods=['GET'])
def get_value():
    global all_flashcards

    user_input = request.args.get('user_string', type=str)
    insert_or_not = request.args.get('insertOrNot', default=1, type=int)
    user_id = request.args.get('user_id', default=0, type=int)

    results = []

    if insert_or_not == 1:
        # Insert: handle multiple flashcards by splitting on newlines
        if user_input:
            lines = user_input.split('\n')
            for line in lines:
                line = line.strip()
                if line:  # Avoid empty lines
                    frequencies = compute_frequencies(line)
                    card = {
                        'id': user_id,
                        'frequencies': frequencies,
                        'content': line
                    }
                    all_flashcards.append(card)
                    save_flashcards(all_flashcards)

        results = [
            f"[ID: {card['id']}, Frequencies: {card['frequencies']}] {card['content']}"
            for card in all_flashcards
        ]

    elif insert_or_not == 0:
        # Search
        if not user_input:
            results = [
                f"[ID: {card['id']}, Frequencies: {card['frequencies']}] {card['content']}"
                for card in all_flashcards
            ]
        else:
            input_words = re.findall(r'\w+', user_input.lower())
            expanded_query_words = expand_with_synonyms(input_words)

            scored_cards = []
            for card in all_flashcards:
                doc_len = sum(card['frequencies'].values())
                score = bm25_score(expanded_query_words, card['frequencies'], doc_len)
                if score > 0:
                    scored_cards.append((score, card))

            # Sort descending by score
            scored_cards.sort(key=lambda x: x[0], reverse=True)  # Sort by score (first element of tuple)
            results = [
                f"[ID: {card['id']}, Frequencies: {card['frequencies']}] {card['content']}"
                for score, card in scored_cards
            ]

    # If browser
    if 'text/html' in request.headers.get('Accept', ''):
        return render_template_string(form_html, values=results)

    # Otherwise JSON
    return jsonify({'strings': results})
