module Esi
  class JitaVolumeVerification < Download

    def check

      item_cpp_ids = [ 41270, 2679, 24486 ]
      jita_cpp_id = 10000002

      item_cpp_ids.each do |id|
        history_volume = 0

        @params[:type_id] = id
        @rest_url = "markets/#{jita_cpp_id}/history/"

        get_all_pages.each do |page|
          date = DateTime.parse( page['date'] )

          next if date < Time.now - 30.days

          # p date

          history_volume += page['volume']
          # pp p:ge
        end

        e_id = EveItem.find_by_cpp_eve_item_id( id )
        t_id = TradeHub.find_by_eve_system_id( 30000142 )

        pa = PricesAdvice.where( trade_hub_id: t_id.id, eve_item_id: e_id.id ).first

        # pp PricesAdvice.where( trade_hub_id: t_id.id, eve_item_id: e_id.id ).all

        pa_vm = pa.vol_month.nil? ? 1 : pa.vol_month

        hv = ActionController::Base.helpers.number_to_human history_volume
        vm = ActionController::Base.helpers.number_to_human pa_vm

        # p pa

        puts "#{e_id.name} - monthly db volume / monthly history volume : #{vm} / #{hv}, pourcentage : #{((pa_vm*100.0)/history_volume).round} %"
        puts

      end
    end
  end
end
