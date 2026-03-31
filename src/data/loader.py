import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")
log = logging.getLogger(__name__)

SD_DIR = Path("data/sd")
MM_DIR = Path("data/mm")

HEADERS = {
    "SalesOrderHeader": [
        "SalesOrderID","RevisionNumber","OrderDate","DueDate","ShipDate",
        "Status","OnlineOrderFlag","SalesOrderNumber","PurchaseOrderNumber",
        "AccountNumber","CustomerID","SalesPersonID","TerritoryID",
        "BillToAddressID","ShipToAddressID","ShipMethodID","CreditCardID",
        "CreditCardApprovalCode","CurrencyRateID","SubTotal","TaxAmt",
        "Freight","TotalDue","Comment","rowguid","ModifiedDate"
    ],
    "SalesOrderDetail": [
        "SalesOrderID","SalesOrderDetailID","CarrierTrackingNumber",
        "OrderQty","ProductID","SpecialOfferID","UnitPrice",
        "UnitPriceDiscount","LineTotal","rowguid","ModifiedDate"
    ],
    "Customer": [
        "CustomerID","PersonID","StoreID","TerritoryID",
        "AccountNumber","rowguid","ModifiedDate"
    ],
    "Product": [
        "ProductID","Name","ProductNumber","MakeFlag","FinishedGoodsFlag",
        "Color","SafetyStockLevel","ReorderPoint","StandardCost","ListPrice",
        "Size","SizeUnitMeasureCode","WeightUnitMeasureCode","Weight",
        "DaysToManufacture","ProductLine","Class","Style",
        "ProductSubcategoryID","ProductModelID","SellStartDate",
        "SellEndDate","DiscontinuedDate","rowguid","ModifiedDate"
    ],
    "ProductInventory": [
        "ProductID","LocationID","Shelf","Bin","Quantity",
        "rowguid","ModifiedDate"
    ],
    "PurchaseOrderHeader": [
        "PurchaseOrderID","RevisionNumber","Status","EmployeeID",
        "VendorID","ShipMethodID","OrderDate","ShipDate",
        "SubTotal","TaxAmt","Freight","TotalDue","ModifiedDate"
    ],
    "PurchaseOrderDetail": [
        "PurchaseOrderID","PurchaseOrderDetailID","DueDate","OrderQty",
        "ProductID","UnitPrice","LineTotal","ReceivedQty",
        "RejectedQty","StockedQty","ModifiedDate"
    ],
}

DROP_COLS = ["rowguid", "ModifiedDate", "Comment", "CreditCardApprovalCode",
             "CurrencyRateID", "RevisionNumber"]


def read_csv(path: Path, name: str) -> pd.DataFrame:
    df = pd.read_csv(
        path, sep="\t", header=None,
        names=HEADERS[name], low_memory=False
    )
    return df


def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if "Date" in col or "date" in col:
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
            except Exception:
                pass
    return df


def drop_unused(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in DROP_COLS if c in df.columns]
    return df.drop(columns=cols)


def load_sales_orders() -> pd.DataFrame:
    log.info("Loading sales orders...")
    header = read_csv(SD_DIR / "SalesOrderHeader.csv", "SalesOrderHeader")
    detail = read_csv(SD_DIR / "SalesOrderDetail.csv", "SalesOrderDetail")
    product = read_csv(MM_DIR / "Product.csv", "Product")[
        ["ProductID", "Name", "ProductNumber"]
    ]

    # Join detail with product names
    detail = detail.merge(product, on="ProductID", how="left")

    # Join header with enriched detail
    df = header.merge(
        detail[["SalesOrderID", "ProductID", "Name",
                "ProductNumber", "OrderQty", "UnitPrice", "LineTotal"]],
        on="SalesOrderID", how="left"
    )

    df = clean_dates(df)
    df = drop_unused(df)
    df["TotalDue"] = df["TotalDue"].round(2)
    df["Status"]   = df["Status"].map({
        1: "In Process", 2: "Approved", 3: "Backordered",
        4: "Rejected",   5: "Shipped",  6: "Cancelled"
    }).fillna("Unknown")

    log.info(f"Sales orders: {len(df)} rows")
    return df


def load_customers() -> pd.DataFrame:
    log.info("Loading customers...")
    df = read_csv(SD_DIR / "Customer.csv", "Customer")
    df = clean_dates(df)
    df = drop_unused(df)
    log.info(f"Customers: {len(df)} rows")
    return df


def load_products() -> pd.DataFrame:
    log.info("Loading products...")
    df = read_csv(MM_DIR / "Product.csv", "Product")
    df = clean_dates(df)
    df = drop_unused(df)
    df["ListPrice"]     = df["ListPrice"].fillna(0).round(2)
    df["StandardCost"]  = df["StandardCost"].fillna(0).round(2)
    df["Color"]         = df["Color"].fillna("N/A")
    df["ProductLine"]   = df["ProductLine"].fillna("N/A")
    log.info(f"Products: {len(df)} rows")
    return df


def load_stock_levels() -> pd.DataFrame:
    log.info("Loading stock levels...")
    inventory = read_csv(MM_DIR / "ProductInventory.csv", "ProductInventory")
    products  = read_csv(MM_DIR / "Product.csv", "Product")[
        ["ProductID", "Name", "ProductNumber",
         "SafetyStockLevel", "ReorderPoint"]
    ]

    # Aggregate inventory quantity per product across all locations
    inv_agg = inventory.groupby("ProductID")["Quantity"].sum().reset_index()
    inv_agg.columns = ["ProductID", "TotalQuantity"]

    df = inv_agg.merge(products, on="ProductID", how="left")
    df["BelowSafety"]  = df["TotalQuantity"] < df["SafetyStockLevel"]
    df["NeedsReorder"] = df["TotalQuantity"] < df["ReorderPoint"]
    df = clean_dates(df)
    log.info(f"Stock levels: {len(df)} rows")
    return df


def load_purchase_orders() -> pd.DataFrame:
    log.info("Loading purchase orders...")
    header  = read_csv(MM_DIR / "PurchaseOrderHeader.csv", "PurchaseOrderHeader")
    detail  = read_csv(MM_DIR / "PurchaseOrderDetail.csv", "PurchaseOrderDetail")
    product = read_csv(MM_DIR / "Product.csv", "Product")[
        ["ProductID", "Name", "ProductNumber"]
    ]

    detail = detail.merge(product, on="ProductID", how="left")
    df     = header.merge(
        detail[["PurchaseOrderID", "ProductID", "Name",
                "ProductNumber", "OrderQty", "UnitPrice", "LineTotal",
                "ReceivedQty", "RejectedQty", "StockedQty"]],
        on="PurchaseOrderID", how="left"
    )

    df = clean_dates(df)
    df = drop_unused(df)
    df["Status"] = df["Status"].map({
        1: "Pending", 2: "Approved",
        3: "Rejected", 4: "Complete"
    }).fillna("Unknown")
    df["TotalDue"] = df["TotalDue"].round(2)

    log.info(f"Purchase orders: {len(df)} rows")
    return df


def load_and_save_all():
    SD_DIR.mkdir(parents=True, exist_ok=True)
    MM_DIR.mkdir(parents=True, exist_ok=True)

    sales    = load_sales_orders()
    customers = load_customers()
    products  = load_products()
    stock     = load_stock_levels()
    po        = load_purchase_orders()

    sales.to_csv(SD_DIR     / "sales_orders_clean.csv",    index=False)
    customers.to_csv(SD_DIR / "customer_master_clean.csv", index=False)
    products.to_csv(MM_DIR  / "product_master_clean.csv",  index=False)
    stock.to_csv(MM_DIR     / "stock_levels_clean.csv",    index=False)
    po.to_csv(MM_DIR        / "purchase_orders_clean.csv", index=False)

    log.info("All clean files saved.")
    log.info(f"  Sales orders:    {len(sales)}")
    log.info(f"  Customers:       {len(customers)}")
    log.info(f"  Products:        {len(products)}")
    log.info(f"  Stock levels:    {len(stock)}")
    log.info(f"  Purchase orders: {len(po)}")
    log.info(f"  Below safety stock: {int(stock['BelowSafety'].sum())}")


if __name__ == "__main__":
    load_and_save_all()