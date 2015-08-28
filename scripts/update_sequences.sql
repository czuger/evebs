SELECT setval('users_id_seq', (SELECT max(ID)+1 FROM users), false);

SELECT setval('identities_id_seq', (SELECT max(ID)+1 FROM identities), false);