# Setting up the various databases we use
mysql::db { 'acid':
  user     => 'acid',
  password => 'acidpass',
  host     => 'localhost',
}
