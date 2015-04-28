namespace :data_setup do
  desc "Feed trade hubs list"
  task :trade_hubs => :environment do
    puts 'About to create trade hubs'
    system_names = %w( Jita Amarr Rens Dodixie Hek Oursulaert Tash-Murkon Agil Sakht Tuomuta Esescama Amarr Dresi Ordion Zinkon Tash-Murkon Prime Berta Ichoriya Motsu Jita Nourvukaiken Sobaseki Torrinos Oursulaert Arnon Halle Orvolle Stacmon Dodixie Boystin Clellinon Sortet Apanake Agil Rens Lustrevik Pator Hek Teonusude XX9-WV G-0Q86 1-SMEB BWF-ZZ E02-IK 4C-B7X 4GQ-XQ LGK-VP TG-Z23 PC9-AY VSIG-K X-M2LR N5Y-4N 4-CM8I )
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