class Esi::UpdateBlueprints < Esi::Download

  REJECTED_PATTERNS = ['Sansha', 'Gurista', 'Dark Blood', 'Angel', 'Navy', 'Edition', 'Quafe', 'ORE', 'Serpentis',
                       'Blood Raiders', 'Thukker Tribe', 'Kador', 'Amastris', 'Tash-Murkon', 'Nugoeihuvi', 'Wiyrkomi',
                        'Nefantar', 'Krusual', 'Aliastra', 'CONCORD' ]

  def update
    ActiveRecord::Base.transaction do
      load_blueprints
    end
  end

  private

  def load_blueprints
    to_remove_blueprint = []

    blueprints = YAML::load_file('data/blueprints.yaml')
    bp_count = blueprints.count
    bp_processed = 0

    blueprints.each do |b|

      bp_processed += 1

      if bp_processed % 100 == 0
        puts "Processed #{bp_processed}/#{bp_count}"
      end

      b= b[1]

      bp_id = b['blueprintTypeID']

      if  !b['activities']['manufacturing']
        to_remove_blueprint << bp_id
        next
      end

      materials = b['activities']['manufacturing']['materials']
      products = b['activities']['manufacturing']['products']

      if  !materials || !products
        to_remove_blueprint << bp_id
        next
      end

      @rest_url = "universe/types/#{bp_id}/"

      begin
        page = get_page_retry_on_error
      rescue Esi::Errors::NotFound
        next
      end

      unless page['published']
        to_remove_blueprint << bp_id
        next
      end

      REJECTED_PATTERNS.each do |pattern|
        if page['name'] =~ /#{pattern}/
          to_remove_blueprint << bp_id
          next
        end
      end

      bp = Blueprint.where( cpp_blueprint_id: bp_id ).first_or_initialize

      if products.count > 1
        puts 'blueprint produce more than one item'
        pp b
        exit
      end

      product = products.first
      bp.name = page['name']
      bp.nb_runs = b['maxProductionLimit']
      bp.prod_qtt = product['quantity']
      bp.produced_cpp_type_id = product['typeID']

      bp.save!
    end

    Blueprint.where( cpp_blueprint_id: nil ).delete_all
    Blueprint.where( cpp_blueprint_id: to_remove_blueprint ).delete_all
  end

  # Rechercher et exclure tout ce qui est navy, gurista, etc ...

end