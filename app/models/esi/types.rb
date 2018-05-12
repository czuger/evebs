class Esi::Types < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )
    # p @errors_limit_remain
  end

  def update
    new_ids = TypeInRegion.distinct.pluck( :cpp_type_id )

    current_cpp_eve_item_ids = EveItem.pluck( :cpp_eve_item_id )
    missing_ids = new_ids - current_cpp_eve_item_ids



  end
end