# Setting up the various databases we use
mysql::db { 'acidcore':
  user     => 'acid',
  password => 'acidpass',
  host     => 'localhost',
}

mysql::db { 'pypsd':
  user     => 'pyps',
  password => 'marleymoo',
  host     => 'localhost',
}
