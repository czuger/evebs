class Esi::UpdateBlueprints < Esi::Download

  # REJECTED_PATTERNS = ['Sansha', 'Gurista', 'Dark Blood', 'Angel', 'Navy', 'Edition', 'Quafe', 'ORE', 'Serpentis',
  #                      'Blood Raiders', 'Thukker Tribe', 'Kador', 'Amastris', 'Tash-Murkon', 'Nugoeihuvi', 'Wiyrkomi',
  #                       'Nefantar', 'Krusual', 'Aliastra', 'CONCORD' ]

  REJECTED_PATTERNS = []

  def update
    ActiveRecord::Base.transaction do
      load_blueprints
    end
  end

  private

  def load_blueprints
    @to_remove_blueprint = []
    @full_blueprints_id_list = []

    blueprints = YAML::load_file('data/blueprints.yaml')
    bp_count = blueprints.count
    bp_processed = 0

    blueprints.each do |blueprint|

      bp_processed += 1
      if bp_processed % 100 == 0
        puts "Processed #{bp_processed}/#{bp_count}"
      end

      next unless read_blueprint_data( blueprint )
      blueprint_type = download_produced_item_data
      next unless blueprint_type

      bp = blueprint_update( blueprint_type )
      next unless process_materials( bp )
    end

    Blueprint.where( cpp_blueprint_id: nil ).delete_all
    Blueprint.where( cpp_blueprint_id: @to_remove_blueprint ).delete_all
    Blueprint.where.not( cpp_blueprint_id: @full_blueprints_id_list ).delete_all

    BlueprintMaterial.where.not( blueprint_id: Blueprint.select( :id ) ).delete_all
    BlueprintComponent.where.not( id: BlueprintMaterial.select( :blueprint_component_id ) ).delete_all

  end

  private

  def read_blueprint_data( blueprint )
    @blueprint= blueprint[1]

    @bp_id = @blueprint['blueprintTypeID']
    @full_blueprints_id_list << @bp_id

     unless @blueprint['activities']['manufacturing']
      @to_remove_blueprint << @bp_id
      return false
    end

    @materials = @blueprint['activities']['manufacturing']['materials']
    @products = @blueprint['activities']['manufacturing']['products']

    if  !@materials || !@products
      @to_remove_blueprint << @bp_id
      return false
    end

    true
  end

  def download_produced_item_data
    @rest_url = "universe/types/#{@bp_id}/"

    begin
      page = get_page_retry_on_error
    rescue Esi::Errors::NotFound
      return false
    end

    unless page['published']
      @to_remove_blueprint << @bp_id
      return false
    end

    REJECTED_PATTERNS.each do |pattern|
      if page['name'] =~ /#{pattern}/
        @to_remove_blueprint << @bp_id
        return false
      end
    end

    page
  end

  def blueprint_update( blueprint_type )
    bp = Blueprint.where( cpp_blueprint_id: @bp_id ).first_or_initialize

    if @products.count > 1
      puts 'blueprint produce more than one item'
      pp b
      exit
    end

    product = @products.first
    bp.name = blueprint_type['name']
    bp.nb_runs = @blueprint['maxProductionLimit']
    bp.prod_qtt = product['quantity']
    bp.produced_cpp_type_id = product['typeID']

    bp.save!
    bp
  end

  # Process materials part
  def process_materials( blueprint )
    @materials.each do |material|
      t_id = material['typeID']

      comp = BlueprintComponent.find_by_cpp_eve_item_id( t_id )
      if !comp || comp.updated_at < Time.now

        @rest_url = "universe/types/#{t_id}/"

        begin
          local_page = get_page_retry_on_error
        rescue Esi::Errors::NotFound
          return false
        end

        comp = BlueprintComponent.where( cpp_eve_item_id: t_id ).first_or_initialize
        comp.name = local_page['name']
        comp.volume = local_page['volume']
        comp.save!
      end

      ar_material = BlueprintMaterial.where(blueprint_id: blueprint.id, blueprint_component_id: comp.id ).first_or_initialize
      ar_material.required_qtt = material['quantity']
      ar_material.save!
    end
  end

end