import requests
from app import db
from models import User, Userlist, Episode, Anime

# Drop and create all tables
db.drop_all()
db.create_all()

# Get data from Kitsu API
anime_data = requests.get('https://kitsu.io/api/edge/anime').json()['data']

# Create Anime instances and save to database
for anime in anime_data:
    subtypes = anime['attributes'].get('subtypes', [])
    new_anime = Anime(title=anime['attributes']['canonicalTitle'],
                      genre=''.join(subtypes),
                      episode_count=anime['attributes']['episodeCount'],
                      rating=anime['attributes']['averageRating'])
    db.session.add(new_anime)

# Create Episode instances for first anime and save to database
episode_data = anime_data[0].get('links', {}).get('episodes')
if episode_data is not None and episode_data:
    episode_data = requests.get(episode_data).json()['data']
    for episode in episode_data:
        new_episode = Episode(title=episode['attributes']['canonicalTitle'], 
                              number=episode['attributes']['indexNumber'], 
                              description=episode['attributes']['synopsis'], 
                              anime=Anime.query.filter_by(title=anime_data[0]['attributes']['canonicalTitle']).first())
        db.session.add(new_episode)

# Commit changes to database
db.session.commit()

# Close database connection
db.session.close()