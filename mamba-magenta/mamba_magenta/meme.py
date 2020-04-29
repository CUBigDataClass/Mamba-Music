x = ['blues', 'folk', 'earth', 'motown', 'post-disco', 'post-grunge', 'jazz', 'gold', 'house', 'country', 'punk', 'guitar', 'pop', 'disco', 'soul', 'rock', 'tunes', 'metal', 'bluegrass', 'indie', 'nederpop', 'levenslied', 'era', 'beats', 'broadway', 'funk', 'standards', 'zillertal', 'trap', 'dawn', 'hop', 'eurodance', 'enfants', 'trance', 'rap', 'freestyle', 'yodeling', 'orchestra', 'novelty', 'sound', 'mezmur', 'reggae', 'classical', 'cv', 'urban', 'singer-songwriter', 'contemporary', 'chill', 'band', 'latino', 'dixieland', 'psytrance', 'fusion', 'ye', 'brasileiro', 'worship', 'schlager', 'music', "d'autore", 'advocacy', 'comic', 'synthpop', 'britpop', 'merseybeat', 'techno', 'psychill', 'liedermacher', 'rockabilly', 'chanson', 'latin', 'disney', 'lilith', 'rock-and-roll', 'world', 'indietronica', 'punta', 'post-rock', 'swing', 'spytrack', 'electronic', 'listening', 'adoracao', 'organ', 'gabba', 'austropop', 'steampunk', 'gospel', 'stride', 'romanticism', 'piano', 'quartet', 'mexican', 'sleep', 'alley', 'hardcore', 'cristiano', 'storm', 'electropop', 'revival', 'american', 'nova', 'beat', 'bass', 'quebecois', 'flow', 'flamenco', 'caipira', 'anarcho-punk', 'r&b', 'doo-wop', 'volksmusik', 'ska', 'invasion', 'europop', 'dance', 'instrumental', 'cappella', 'soundtrack', 'freakbeat', 'dub', 'metropopolis', 'karneval', 'romantico', 'hollywood', 'paraguaya', 'cover', 'edm', 'hi-nrg', 'dansktop', 'show', 'universitario', 'tenor', 'banjo', 'age', 'pagode', 'shaabi', 'garage', 'monastic', 'downtempo', 'banda', 'traprun', 'americana', 'zither', 'mellow', 'idol', 'ragtime', 'metalcore', 'cabaret', 'environmental']

master_list = []
for key in genres_mapping:
    x1 = genres_mapping[key]
    for val in x1:
        if val in master_list:
            print(val)
    master_list.extend(x1)
print(len(master_list))
