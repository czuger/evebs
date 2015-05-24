namespace :data_setup do
  desc "Feed trade hubs list"
  task :create_first_user => :environment do
    puts 'Creating the first user'
    User.find_or_create_by!( name: 'test' )
  end

  desc "Create public user"
  task :create_public_user => :environment do
    puts 'Creating the public user'
    u=User.find_or_create_by!( name: 'PUBLIC_USER' )
    jita=TradeHub.find_by_name('Jita')
    u.trade_hubs=[jita]
    pu_items_cpp_names=File.open('lib/tasks/public_user_items.txt','r').readlines
    pu_items=[]
    pu_items_cpp_names.each do |name|
      name=name.strip
      # puts "About to add #{name.inspect}"
      item = EveItem.find_by_name(name)
      pu_items << item if item
    end
    # puts pu_items.inspect
    u.eve_items=pu_items
  end

end