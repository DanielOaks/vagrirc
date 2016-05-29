# MySQL core configuration
class { '::mysql::server':
  root_password => 'password',
  remove_default_accounts => true,
}
