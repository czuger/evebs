class Blueprint < ActiveRecord::Base
  belongs_to :eve_item
  has_many :materials
  validates :eve_item_id, :nb_runs, :prod_qtt, :cpp_blueprint_id, presence: true

  # We don't process some blueprint, because they leads to issues
  UNWANTED_BLUEPRINTS = [3927,34189,34497]

  def batch_elements_count
    prod_qtt*nb_runs
  end

  def self.load_blueprint_array
    blueprints_array = []
    blueprint_files=YAML.load_file('lib/tasks/blueprints.yaml')
    blueprint_files.each do |bp_id,bp|
      if bp['activities']['manufacturing']
        blueprint_id = bp_id
        manufacturing = bp['activities']['manufacturing']
        produced_item_id = manufacturing['products'].first['typeID']
        produced_item_qtt = manufacturing['products'].first['quantity']
        max_production_limit = bp['maxProductionLimit']
        skills = bp['activities']['manufacturing']['skills']
        blueprints_array << {
            blueprint_id: blueprint_id, produced_item_id: produced_item_id, produced_item_qtt: produced_item_qtt,
            max_production_limit: max_production_limit,
            materials: manufacturing['materials'],
            skills_count: skills ? skills.count : 0
        }
      end
    end
    blueprints_array
  end
end
