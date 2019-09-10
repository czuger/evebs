# This class is linked to a temporary table, in PGSQL temporary table are created
# and dropped at the end of the session. That's why you can't see the table on PGSQL

class EveMarketHistoriesGroupTmpTable < ApplicationRecord
end