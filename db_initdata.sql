LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('hehuan2112@gmail.com','pbkdf2:sha256:150000$oHLnajng$9be224b50b962de1d83cd745124fc6fe6828e5079c560fa6654d668439b77503','Huan','He','user','no'),('sipra.irbaz@gmail.com','pbkdf2:sha256:150000$oHLnajng$9be224b50b962de1d83cd745124fc6fe6828e5079c560fa6654d668439b77503','Irbaz','Riaz','user','no');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;