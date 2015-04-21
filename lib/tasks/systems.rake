namespace :data_setup do
  desc "Feed trade hubs list"
  task :trade_hubs => :environment do
    puts 'About to create trade hubs'
    system_names = %w( Teonusude Hek Jita Rens Pator Amarr Dodixie Gelfiven Lustrevik Eram Orvolle Stacmon )
    api = EAAL::API.new(nil,nil)
    api.scope = "eve"

    for system_name in system_names.sort
      unless TradeHub.find_by_name( system_name )
        puts "Creating entry for #{system_name}"
        result = api.CharacterID(:names => system_name)
        system_id = result.characters.first.characterID.to_i
        raise "Unable to find system for system_name #{system_name}" if system_id.nil? || system_id == 0
        TradeHub.find_or_create_by( name: system_name, eve_system_id: system_id )
      end
    end
  end
end