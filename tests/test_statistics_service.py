import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from services.statistics_service import StatisticsService
from database.repo import DBRepository
from database.models import User, Operation


@pytest.fixture(autouse=True)
def setup_redis_mock(redis_client):
    """Automatically patch redis_client in StatisticsService for all tests."""
    with patch("services.statistics_service.redis_client", redis_client):
        yield


class TestStatisticsService:

    @pytest.mark.asyncio
    async def test_get_base_stat_with_operations(
        self, repo: DBRepository, test_user: User, test_operations: list[Operation], mock_internal_keywords
    ):
        service = StatisticsService()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime(2026, 4, 1),
            end_date=datetime(2026, 4, 30)
        )
        
        assert stats["salary"] == 100000.0
        assert stats["sum_income"] == 108000.0
        assert stats["sum_expense"] == 32000.0
        assert stats["balance"] == 76000.0
        assert stats["income_count"] == 3
        assert stats["expense_count"] == 7
        assert stats["transactions_count"] == 10
        assert stats["internal_transfers_excluded"] == 2
    
    @pytest.mark.asyncio
    async def test_get_base_stat_empty_operations(self, repo: DBRepository, test_user: User):
        service = StatisticsService()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id
        )
        
        assert stats["salary"] == 0
        assert stats["sum_income"] == 0
        assert stats["sum_expense"] == 0
        assert stats["balance"] == 0
        assert stats["avg_expense"] == 0
        assert stats["transactions_count"] == 0
        assert stats["income_count"] == 0
        assert stats["expense_count"] == 0
    
    @pytest.mark.asyncio
    async def test_get_base_stat_with_date_filter(
        self, repo: DBRepository, test_user: User, test_operations: list[Operation], mock_internal_keywords
    ):
        service = StatisticsService()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime(2026, 4, 1),
            end_date=datetime(2026, 4, 5)
        )
        
        assert stats["salary"] == 100000.0
        assert stats["sum_income"] == 108000.0
        assert stats["sum_expense"] == 8000.0
        assert stats["expense_count"] == 2
    
    @pytest.mark.asyncio
    async def test_get_base_stat_with_category_filter(
        self, repo: DBRepository, test_user: User, test_operations: list[Operation], mock_internal_keywords
    ):
        service = StatisticsService()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime(2026, 4, 1),
            end_date=datetime(2026, 4, 30),
            categories=["Продукты"]
        )
        
        assert stats["sum_expense"] == 10000.0
        assert stats["expense_count"] == 3
        assert stats["sum_income"] == 0
    
    @pytest.mark.asyncio
    async def test_internal_transfer_filtering(
        self, repo: DBRepository, test_user: User, test_operations: list[Operation], mock_internal_keywords
    ):
        service = StatisticsService()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime(2026, 4, 1),
            end_date=datetime(2026, 4, 30)
        )
        
        assert stats["internal_transfers_excluded"] == 2
        assert stats["balance"] == 76000.0
    
    @pytest.mark.asyncio
    async def test_avg_expense_calculation(
        self, repo: DBRepository, test_user: User, test_operations: list[Operation], mock_internal_keywords
    ):
        service = StatisticsService()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime(2026, 4, 1),
            end_date=datetime(2026, 4, 30)
        )
        
        # avg_expense = total_expense / expense_count = 32000 / 7
        expected_avg = round(32000.0 / 7, 2)
        assert stats["avg_expense"] == expected_avg
    
    @pytest.mark.asyncio
    async def test_get_categories_stat(
        self, repo: DBRepository, test_user: User, test_operations: list[Operation], mock_internal_keywords
    ):
        service = StatisticsService()
        
        categories = await service.get_categories_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime(2026, 4, 1),
            end_date=datetime(2026, 4, 30)
        )
        
        assert "Развлечения" in categories["top_expense_categories"]
        assert "Продукты" in categories["top_expense_categories"]
        assert "Транспорт" in categories["top_expense_categories"]
        
        assert categories["top_expense_categories"]["Развлечения"]["amount"] == 20000.0
        assert categories["top_expense_categories"]["Продукты"]["amount"] == 10000.0
        assert categories["top_expense_categories"]["Транспорт"]["amount"] == 2000.0
        
        total_expense = 32000.0
        assert categories["top_expense_categories"]["Развлечения"]["percentage"] == round((20000 / total_expense) * 100, 2)
    
    @pytest.mark.asyncio
    async def test_get_categories_stat_empty(self, repo: DBRepository, test_user: User):
        service = StatisticsService()
        
        categories = await service.get_categories_stat(
            repo=repo,
            user_id=test_user.tg_id
        )
        
        assert categories["top_expense_categories"] == {}
        assert categories["top_income_categories"] == {}
    
    @pytest.mark.asyncio
    async def test_salary_category_recognition(
        self, repo: DBRepository, test_user: User, test_operations: list[Operation], mock_internal_keywords
    ):
        service = StatisticsService()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime(2026, 4, 1),
            end_date=datetime(2026, 4, 30)
        )
        
        assert stats["salary"] == 100000.0
        assert stats["sum_income"] >= stats["salary"]
    
    @pytest.mark.asyncio
    async def test_rounding_precision(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        service = StatisticsService()
        
        op = Operation(
            user_id=test_user.tg_id,
            amount=-123.456,
            is_income=False,
            raw_category="Test",
            description="Test",
            date=datetime(2026, 4, 1),
            bank_name="test",
            currency="RUB"
        )
        repo.session.add(op)
        await repo.session.commit()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime(2026, 4, 1),
            end_date=datetime(2026, 4, 30)
        )
        
        assert isinstance(stats["sum_expense"], float)
        assert len(str(stats["sum_expense"]).split(".")[-1]) <= 2
        assert stats["sum_expense"] == 123.46


class TestStatisticsServiceCaching:

    @pytest.mark.asyncio
    async def test_cache_hit(
        self, repo: DBRepository, test_user: User, test_operations: list[Operation], 
        redis_client, mock_internal_keywords
    ):
        service = StatisticsService()
        
        with patch("services.statistics_service.redis_client", redis_client):
            stats1 = await service.get_base_stat(
                repo=repo,
                user_id=test_user.tg_id,
                start_date=datetime(2026, 4, 1),
                end_date=datetime(2026, 4, 30)
            )
            
            stats2 = await service.get_base_stat(
                repo=repo,
                user_id=test_user.tg_id,
                start_date=datetime(2026, 4, 1),
                end_date=datetime(2026, 4, 30)
            )
            
            assert stats1 == stats2
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_on_version_change(
        self, repo: DBRepository, test_user: User, test_operations: list[Operation],
        redis_client, mock_internal_keywords
    ):
        service = StatisticsService()
        
        with patch("services.statistics_service.redis_client", redis_client):
            stats1 = await service.get_base_stat(
                repo=repo,
                user_id=test_user.tg_id,
                start_date=datetime(2026, 4, 1),
                end_date=datetime(2026, 4, 30)
            )
            
            version_key = f"user:{test_user.tg_id}:version"
            await redis_client.redis.incr(version_key)
            
            stats2 = await service.get_base_stat(
                repo=repo,
                user_id=test_user.tg_id,
                start_date=datetime(2026, 4, 1),
                end_date=datetime(2026, 4, 30)
            )
            
            assert stats1 == stats2


class TestStatisticsServiceEdgeCases:

    @pytest.mark.asyncio
    async def test_future_date_range(self, repo: DBRepository, test_user: User, test_operations: list[Operation]):
        service = StatisticsService()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime(2027, 1, 1),
            end_date=datetime(2027, 12, 31)
        )
        
        assert stats["transactions_count"] == 0
        assert stats["balance"] == 0
    
    @pytest.mark.asyncio
    async def test_invalid_date_range(self, repo: DBRepository, test_user: User, test_operations: list[Operation]):
        service = StatisticsService()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime(2026, 4, 30),
            end_date=datetime(2026, 4, 1)
        )
        
        # Should return empty stats
        assert stats["transactions_count"] == 0
    
    @pytest.mark.asyncio
    async def test_nonexistent_category_filter(
        self, repo: DBRepository, test_user: User, test_operations: list[Operation]
    ):
        service = StatisticsService()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime(2026, 4, 1),
            end_date=datetime(2026, 4, 30),
            categories=["NonExistentCategory"]
        )
        
        assert stats["transactions_count"] == 0
        assert stats["sum_expense"] == 0


class TestStatisticsServiceAutoDateRange:
    """Test automatic date range detection."""
    
    @pytest.mark.asyncio
    async def test_auto_date_range_with_recent_operations(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test auto date range when operations exist in last 30 days."""
        service = StatisticsService()
        
        # Add recent operation
        recent_op = Operation(
            user_id=test_user.tg_id,
            amount=-1000.0,
            is_income=False,
            raw_category="Test",
            description="Recent",
            date=datetime.now() - timedelta(days=5),
            bank_name="test",
            currency="RUB"
        )
        repo.session.add(recent_op)
        await repo.session.commit()
        
        # Call without dates - should use last 30 days
        stats = await service.get_base_stat(repo=repo, user_id=test_user.tg_id)
        
        assert stats["transactions_count"] == 1
        assert stats["sum_expense"] == 1000.0
    
    @pytest.mark.asyncio
    async def test_auto_date_range_with_old_operations_only(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test auto date range when all operations are older than 30 days."""
        service = StatisticsService()
        
        # Add old operation (3 months ago)
        old_date = datetime.now() - timedelta(days=90)
        old_op = Operation(
            user_id=test_user.tg_id,
            amount=-5000.0,
            is_income=False,
            raw_category="Test",
            description="Old",
            date=old_date,
            bank_name="test",
            currency="RUB"
        )
        repo.session.add(old_op)
        await repo.session.commit()
        
        # Should use month of last operation
        stats = await service.get_base_stat(repo=repo, user_id=test_user.tg_id)
        
        assert stats["transactions_count"] == 1
        assert stats["sum_expense"] == 5000.0


class TestStatisticsServiceInternalTransfers:
    """Test internal transfer detection logic."""
    
    @pytest.mark.asyncio
    async def test_internal_transfer_case_insensitive(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test that internal transfer keywords are case-insensitive."""
        service = StatisticsService()
        
        operations_data = [
            {"description": "Transfer from МАКСИМ Б", "amount": 5000.0},
            {"description": "Transfer from максим б", "amount": 5000.0},
            {"description": "Transfer from МаКсИм Б", "amount": 5000.0},
        ]
        
        for op_data in operations_data:
            op = Operation(
                user_id=test_user.tg_id,
                amount=op_data["amount"],
                is_income=True,
                raw_category="Переводы",
                description=op_data["description"],
                date=datetime.now(),
                bank_name="test",
                currency="RUB"
            )
            repo.session.add(op)
        
        await repo.session.commit()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1)
        )
        
        # All should be filtered as internal transfers
        assert stats["internal_transfers_excluded"] == 3
        assert stats["sum_income"] == 0
    
    @pytest.mark.asyncio
    async def test_internal_transfer_only_in_transfer_categories(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test that keyword matching only works for transfer categories."""
        service = StatisticsService()
        
        # Same keyword but different category - should NOT be filtered
        op = Operation(
            user_id=test_user.tg_id,
            amount=-1000.0,
            is_income=False,
            raw_category="Продукты",  # Not a transfer category
            description="Store owned by Максим Б",
            date=datetime.now(),
            bank_name="test",
            currency="RUB"
        )
        repo.session.add(op)
        await repo.session.commit()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1)
        )
        
        # Should NOT be filtered
        assert stats["internal_transfers_excluded"] == 0
        assert stats["sum_expense"] == 1000.0
    
    @pytest.mark.asyncio
    async def test_internal_transfer_all_category_variants(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test internal transfer detection for all category variants."""
        service = StatisticsService()
        
        categories = ["Переводы", "Пополнения", "Пополнение"]
        
        for category in categories:
            op = Operation(
                user_id=test_user.tg_id,
                amount=1000.0,
                is_income=True,
                raw_category=category,
                description="Transfer from Максим Б",
                date=datetime.now(),
                bank_name="test",
                currency="RUB"
            )
            repo.session.add(op)
        
        await repo.session.commit()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1)
        )
        
        # All 3 should be filtered
        assert stats["internal_transfers_excluded"] == 3


class TestStatisticsServiceCategoryFiltering:
    """Test category filtering with regex patterns."""
    
    @pytest.mark.asyncio
    async def test_category_filter_multiple_categories(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test filtering by multiple categories."""
        service = StatisticsService()
        
        operations_data = [
            {"category": "Продукты", "amount": -1000.0},
            {"category": "Транспорт", "amount": -500.0},
            {"category": "Развлечения", "amount": -2000.0},
        ]
        
        for op_data in operations_data:
            op = Operation(
                user_id=test_user.tg_id,
                amount=op_data["amount"],
                is_income=False,
                raw_category=op_data["category"],
                description="Test",
                date=datetime.now(),
                bank_name="test",
                currency="RUB"
            )
            repo.session.add(op)
        
        await repo.session.commit()
        
        # Filter by 2 categories
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1),
            categories=["Продукты", "Транспорт"]
        )
        
        assert stats["sum_expense"] == 1500.0  # 1000 + 500
        assert stats["expense_count"] == 2
    
    @pytest.mark.asyncio
    async def test_category_filter_case_insensitive(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test that category filtering is case-insensitive."""
        service = StatisticsService()
        
        op = Operation(
            user_id=test_user.tg_id,
            amount=-1000.0,
            is_income=False,
            raw_category="ПРОДУКТЫ",
            description="Test",
            date=datetime.now(),
            bank_name="test",
            currency="RUB"
        )
        repo.session.add(op)
        await repo.session.commit()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1),
            categories=["продукты"]
        )
        
        assert stats["sum_expense"] == 1000.0
    
    @pytest.mark.asyncio
    async def test_category_filter_partial_match(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test that category filter supports partial matching."""
        service = StatisticsService()
        
        operations_data = [
            {"category": "Продукты питания", "amount": -1000.0},
            {"category": "Продукты для дома", "amount": -500.0},
            {"category": "Транспорт", "amount": -300.0},
        ]
        
        for op_data in operations_data:
            op = Operation(
                user_id=test_user.tg_id,
                amount=op_data["amount"],
                is_income=False,
                raw_category=op_data["category"],
                description="Test",
                date=datetime.now(),
                bank_name="test",
                currency="RUB"
            )
            repo.session.add(op)
        
        await repo.session.commit()
        
        # Filter by partial match "Продукты"
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1),
            categories=["Продукты"]
        )
        
        assert stats["sum_expense"] == 1500.0  # Both "Продукты" categories


class TestStatisticsServiceGetCategoriesStat:
    """Test get_categories_stat method edge cases."""
    
    @pytest.mark.asyncio
    async def test_categories_stat_with_zero_total(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test category percentages when total is zero (all internal transfers)."""
        service = StatisticsService()
        
        # Only internal transfers
        op = Operation(
            user_id=test_user.tg_id,
            amount=5000.0,
            is_income=True,
            raw_category="Переводы",
            description="Transfer from Максим Б",
            date=datetime.now(),
            bank_name="test",
            currency="RUB"
        )
        repo.session.add(op)
        await repo.session.commit()
        
        categories = await service.get_categories_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1)
        )
        
        # Should return empty categories
        assert categories["top_expense_categories"] == {}
        assert categories["top_income_categories"] == {}
    
    @pytest.mark.asyncio
    async def test_categories_stat_top_10_limit(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test that only top 10 categories are returned."""
        service = StatisticsService()
        
        # Create 15 different expense categories
        for i in range(15):
            op = Operation(
                user_id=test_user.tg_id,
                amount=-(i + 1) * 100.0,
                is_income=False,
                raw_category=f"Category_{i}",
                description="Test",
                date=datetime.now(),
                bank_name="test",
                currency="RUB"
            )
            repo.session.add(op)
        
        await repo.session.commit()
        
        categories = await service.get_categories_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1)
        )
        
        # Should return only top 10
        assert len(categories["top_expense_categories"]) == 10
        # Should be sorted by amount descending
        amounts = [v["amount"] for v in categories["top_expense_categories"].values()]
        assert amounts == sorted(amounts, reverse=True)


class TestStatisticsServiceGetSummaryForAI:
    """Test get_summary_for_ai method."""
    
    @pytest.mark.asyncio
    async def test_summary_for_ai_with_data(
        self, repo: DBRepository, test_user: User, test_operations: list[Operation], mock_internal_keywords
    ):
        """Test AI summary generation with data."""
        service = StatisticsService()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime(2026, 4, 1),
            end_date=datetime(2026, 4, 30)
        )
        
        operations = await repo.get_user_operations(test_user.tg_id)
        df = service._filter_statistics_date(operations, datetime(2026, 4, 1), datetime(2026, 4, 30))
        
        summary = service.get_summary_for_ai(stats, df, is_category_filter=False)
        
        assert "Exp:" in summary
        assert "Bal:" in summary
        assert "Salary:" in summary
        assert "Top:" in summary
    
    @pytest.mark.asyncio
    async def test_summary_for_ai_with_category_filter(
        self, repo: DBRepository, test_user: User, test_operations: list[Operation], mock_internal_keywords
    ):
        """Test AI summary with category filter flag."""
        service = StatisticsService()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime(2026, 4, 1),
            end_date=datetime(2026, 4, 30),
            categories=["Продукты"]
        )
        
        operations = await repo.get_user_operations(test_user.tg_id)
        df = service._filter_statistics_date(operations, datetime(2026, 4, 1), datetime(2026, 4, 30))
        
        summary = service.get_summary_for_ai(stats, df, is_category_filter=True)
        
        assert "Income/Refunds:" in summary
        assert "Bal:" not in summary  # Balance not shown for category filter
        assert "Salary:" not in summary  # Salary not shown for category filter
    
    def test_summary_for_ai_empty_data(self):
        """Test AI summary with empty data."""
        service = StatisticsService()
        
        summary = service.get_summary_for_ai({}, pd.DataFrame(), is_category_filter=False)
        
        assert summary == "No data."



class TestStatisticsServiceDataIntegrity:
    """Test data integrity and special values handling."""
    
    @pytest.mark.asyncio
    async def test_operations_with_null_description(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test handling operations with NULL description."""
        service = StatisticsService()
        
        op = Operation(
            user_id=test_user.tg_id,
            amount=-1000.0,
            is_income=False,
            raw_category="Test",
            description=None,  # NULL description
            date=datetime.now(),
            bank_name="test",
            currency="RUB"
        )
        repo.session.add(op)
        await repo.session.commit()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1)
        )
        
        assert stats["sum_expense"] == 1000.0
        assert stats["transactions_count"] == 1
    
    @pytest.mark.asyncio
    async def test_operations_with_null_category(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test handling operations with NULL category."""
        service = StatisticsService()
        
        op = Operation(
            user_id=test_user.tg_id,
            amount=-1000.0,
            is_income=False,
            raw_category=None,  # NULL category
            description="Test",
            date=datetime.now(),
            bank_name="test",
            currency="RUB"
        )
        repo.session.add(op)
        await repo.session.commit()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1)
        )
        
        assert stats["sum_expense"] == 1000.0
    
    @pytest.mark.asyncio
    async def test_operations_with_very_large_amounts(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test handling very large amounts."""
        service = StatisticsService()
        
        op = Operation(
            user_id=test_user.tg_id,
            amount=-999999999.99,
            is_income=False,
            raw_category="Test",
            description="Large amount",
            date=datetime.now(),
            bank_name="test",
            currency="RUB"
        )
        repo.session.add(op)
        await repo.session.commit()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1)
        )
        
        assert stats["sum_expense"] == 999999999.99
        assert isinstance(stats["sum_expense"], float)
    
    @pytest.mark.asyncio
    async def test_operations_with_very_small_amounts(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test handling very small amounts (cents)."""
        service = StatisticsService()
        
        op = Operation(
            user_id=test_user.tg_id,
            amount=-0.01,
            is_income=False,
            raw_category="Test",
            description="Small amount",
            date=datetime.now(),
            bank_name="test",
            currency="RUB"
        )
        repo.session.add(op)
        await repo.session.commit()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1)
        )
        
        assert stats["sum_expense"] == 0.01
    
    @pytest.mark.asyncio
    async def test_mixed_income_expense_same_category(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test category with both income and expense operations."""
        service = StatisticsService()
        
        # Income in "Прочее"
        op1 = Operation(
            user_id=test_user.tg_id,
            amount=5000.0,
            is_income=True,
            raw_category="Прочее",
            description="Refund",
            date=datetime.now(),
            bank_name="test",
            currency="RUB"
        )
        # Expense in "Прочее"
        op2 = Operation(
            user_id=test_user.tg_id,
            amount=-3000.0,
            is_income=False,
            raw_category="Прочее",
            description="Other expense",
            date=datetime.now(),
            bank_name="test",
            currency="RUB"
        )
        repo.session.add_all([op1, op2])
        await repo.session.commit()
        
        categories = await service.get_categories_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1)
        )
        
        # Should appear in both income and expense categories
        assert "Прочее" in categories["top_income_categories"]
        assert "Прочее" in categories["top_expense_categories"]
        assert categories["top_income_categories"]["Прочее"]["amount"] == 5000.0
        assert categories["top_expense_categories"]["Прочее"]["amount"] == 3000.0
    
    @pytest.mark.asyncio
    async def test_operations_on_boundary_dates(
        self, repo: DBRepository, test_user: User, mock_internal_keywords
    ):
        """Test operations exactly on start_date and end_date boundaries."""
        service = StatisticsService()
        
        start = datetime(2026, 4, 1, 0, 0, 0)
        end = datetime(2026, 4, 30, 23, 59, 59)
        
        # Operation exactly at start
        op1 = Operation(
            user_id=test_user.tg_id,
            amount=-1000.0,
            is_income=False,
            raw_category="Test",
            description="At start",
            date=start,
            bank_name="test",
            currency="RUB"
        )
        # Operation exactly at end
        op2 = Operation(
            user_id=test_user.tg_id,
            amount=-2000.0,
            is_income=False,
            raw_category="Test",
            description="At end",
            date=end,
            bank_name="test",
            currency="RUB"
        )
        # Operation just before start
        op3 = Operation(
            user_id=test_user.tg_id,
            amount=-500.0,
            is_income=False,
            raw_category="Test",
            description="Before start",
            date=start - timedelta(seconds=1),
            bank_name="test",
            currency="RUB"
        )
        # Operation just after end
        op4 = Operation(
            user_id=test_user.tg_id,
            amount=-500.0,
            is_income=False,
            raw_category="Test",
            description="After end",
            date=end + timedelta(seconds=1),
            bank_name="test",
            currency="RUB"
        )
        
        repo.session.add_all([op1, op2, op3, op4])
        await repo.session.commit()
        
        stats = await service.get_base_stat(
            repo=repo,
            user_id=test_user.tg_id,
            start_date=start,
            end_date=end
        )
        
        assert stats["sum_expense"] == 3000.0 
        assert stats["transactions_count"] == 2
