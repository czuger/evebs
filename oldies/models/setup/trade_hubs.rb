class Setup::TradeHubs

  SYSTEM_NAMES = %w( Jita Amarr Rens Dodixie Hek Oursulaert Tash-Murkon Agil Sakht Tuomuta Esescama Amarr Dresi Ordion Zinkon Tash-Murkon Prime Berta Ichoriya Motsu Jita Nourvukaiken Sobaseki Torrinos Oursulaert Arnon Halle Orvolle Stacmon Dodixie Boystin Clellinon Sortet Apanake Agil Rens Lustrevik Pator Hek Teonusude XX9-WV G-0Q86 1-SMEB BWF-ZZ E02-IK 4C-B7X 4GQ-XQ LGK-VP TG-Z23 PC9-AY VSIG-K X-M2LR N5Y-4N 4-CM8I )

  def initialize

    api = EAAL::API.new(nil,nil)
    api.scope = 'eve'

    ActiveRecord::Base.transaction do

      for system_name in SYSTEM_NAMES.sort
        unless TradeHub.find_by_name( system_name )
          puts "Creating entry for #{system_name}" unless Rails.env == 'test'
          result = api.CharacterID(:names => system_name)
          system_id = result.characters.first.characterID.to_i
          raise "Unable to find system for system_name #{system_name}" if system_id.nil? || system_id == 0
          TradeHub.find_or_create_by( name: system_name, eve_system_id: system_id )
        end
      end

      update_inner
    end


  end

  private

  def update_inner

    ActiveRecord::Base.transaction do
      TradeHub.all.each do |trade_hub|
        if trade_hub.name.match( /.+-.+/ )
          trade_hub.update_attribute( :inner, false )
        else
          trade_hub.update_attribute( :inner, true )
        end
      end
    end
  end
end