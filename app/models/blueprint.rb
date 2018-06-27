class Blueprint < ApplicationRecord

  extend Setup::UpdateBlueprints

  # belongs_to :produced
  has_many :materials

  # We don't process some blueprint, because they leads to issues
  UNWANTED_BLUEPRINTS = [3927,34189,34497]

  def batch_elements_count
    prod_qtt*nb_runs
  end

end