namespace :load do
  desc "Feed trade hubs list"
  task :create_first_user => :environment do
    User.create( name: 'test' )
  end
end