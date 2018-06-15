class Esi::UpdateStructures < Esi::Download

  def initialize( debug_request: false )
    super( 'universe/structures/', {}, debug_request: debug_request )
  end

  def update

    Banner.p 'About to update the structures.'

    set_auth_token

    structures_ids = get_all_pages

    puts "#{structures_ids.count} count."

    structures_ids -= Structure.pluck( :cpp_structure_id )

    puts "#{structures_ids.count} remaining count."

    # ActiveRecord::Base.transaction do
      structures_ids.each do |structure_id|

        @rest_url = "universe/structures/#{structure_id.to_s}/"
        forbidden = false
        structure_data = nil

        loop do
          retest = false
          begin
            structure_data = get_page
          rescue Esi::Errors::Forbidden
            forbidden = true
          rescue Esi::Errors::Base => e
            puts "Got #{e.inspect}"
            retest = true
            sleep 10
          rescue => e
            p e
            exit
          end
          break unless retest
        end

        # p "#{@errors_limit_remain}, #{@errors_limit_reset}"

        db_structure = Structure.where( cpp_structure_id: structure_id ).first_or_initialize
        db_structure.forbidden = forbidden

        unless forbidden
          db_structure.trade_hub_id = TradeHub.find_by_eve_system_id( structure_data['solar_system_id'] )
        end

        db_structure.save!

      end
    # end
  end
end