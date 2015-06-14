# Setting up the various databases we use
mysql::db { 'acidcore':
  user     => 'acid',
  password => 'acidpass',
  host     => 'localhost',
}
