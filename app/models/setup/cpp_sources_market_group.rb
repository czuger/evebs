class Setup::CppSourcesMarketGroup < ApplicationRecord

  self.table_name = 'invMarketGroups'

  establish_connection :cpp_original_data

end