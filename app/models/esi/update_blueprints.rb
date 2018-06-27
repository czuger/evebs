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
    @to_remove_blueprint = []

    blueprints = YAML::load_file('data/blueprints.yaml')
    bp_count = blueprints.count
    bp_processed = 0

    blueprints.each do |blueprint|

      bp_processed += 1
      if bp_processed % 100 == 0
        puts "Processed #{bp_processed}/#{bp_count}"
      end

      next unless read_blueprint_data( blueprint )
      next unless download_produced_item_data
      bp = blueprint_update
      next unless process_materials( bp )
    end

    Blueprint.where( cpp_blueprint_id: nil ).delete_all
    Blueprint.where( cpp_blueprint_id: @to_remove_blueprint ).delete_all

    Material.where.not( blueprint_id: Blueprint.select( :id ) ).delete_all
    Component.where.not( id: Material.select( :component_id ) ).delete_all

  end

  private

  def read_blueprint_data( blueprint )
    @blueprint= blueprint[1]

    @bp_id = @blueprint['blueprintTypeID']

    if  !@blueprint['activities']['manufacturing']
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
      @page = get_page_retry_on_error
    rescue Esi::Errors::NotFound
      return false
    end

    unless @page['published']
      @to_remove_blueprint << @bp_id
      return false
    end

    REJECTED_PATTERNS.each do |pattern|
      if @page['name'] =~ /#{pattern}/
        @to_remove_blueprint << @bp_id
        return false
      end
    end

    true
  end

  def blueprint_update
    bp = Blueprint.where( cpp_blueprint_id: @bp_id ).first_or_initialize

    if @products.count > 1
      puts 'blueprint produce more than one item'
      pp b
      exit
    end

    product = @products.first
    bp.name = @page['name']
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

      comp = Component.find_by_cpp_eve_item_id( t_id )
      unless comp

        @rest_url = "universe/types/#{@bp_id}/"

        begin
          local_page = get_page_retry_on_error
        rescue Esi::Errors::NotFound
          return false
        end

        comp = Component.create!( cpp_eve_item_id: t_id, name: local_page['name'] )
      end

      ar_material = Material.where( blueprint_id: blueprint.id, component_id: comp.id ).first_or_initialize
      ar_material.required_qtt = material['quantity']
      ar_material.save!
    end
  end

end