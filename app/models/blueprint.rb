class Blueprint < ApplicationRecord

  extend Setup::UpdateBlueprints

  belongs_to :eve_item
  has_many :materials
  validates :eve_item_id, :nb_runs, :prod_qtt, presence: true

  # We don't process some blueprint, because they leads to issues
  UNWANTED_BLUEPRINTS = [3927,34189,34497]

  def batch_elements_count
    prod_qtt*nb_runs
  end

  def self.load_blueprints
    to_remove_blueprint = []

    blueprints = YAML::load_file('data/blueprints.yaml')
    blueprints.each do |b|

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

    end

    Blueprint.where( cpp_blueprint_id: nil ).delete_all
    Blueprint.where( cpp_blueprint_id: to_remove_blueprint ).delete_all
  end

end