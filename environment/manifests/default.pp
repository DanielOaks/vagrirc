# MySQL configuration
class { '::mysql::server':
  root_password           => 'password',
  remove_default_accounts => true,
  override_options        => $override_options
}

mysql::db { 'acid':
  user     => 'acid',
  password => 'acidpass',
  host     => 'localhost',
}
