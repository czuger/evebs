namespace :data_setup do
  desc "Feed trade hubs list"
  task :create_first_user => :environment do
    puts 'Creating the first user'
    User.find_or_create_by!( name: 'test' )
  end
end