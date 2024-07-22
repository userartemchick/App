import pickle
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher


names = ["Test User", "Admin"]

usernames = ["test", "admin"]

passwords = ["XXXX", "XXXX"]

hashed_passwords = Hasher(passwords).generate()



with open("hashed_pw.pkl", 'wb') as f:
    pickle.dump(hashed_passwords, f)